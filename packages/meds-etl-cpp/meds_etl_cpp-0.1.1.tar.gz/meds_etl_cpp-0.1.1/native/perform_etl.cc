#include "perform_etl.hh"

#include <bitset>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <queue>
#include <set>
#include <string>
#include <thread>

#include "absl/types/optional.h"
#include "arrow/array/array_binary.h"
#include "arrow/array/array_primitive.h"
#include "arrow/array/builder_binary.h"
#include "arrow/array/builder_nested.h"
#include "arrow/array/builder_primitive.h"
#include "arrow/io/file.h"
#include "arrow/memory_pool.h"
#include "arrow/record_batch.h"
#include "arrow/table.h"
#include "arrow/util/type_fwd.h"
#include "blockingconcurrentqueue.h"
#include "lightweightsemaphore.h"
#include "parquet/arrow/reader.h"
#include "parquet/arrow/schema.h"
#include "parquet/arrow/writer.h"
#include "zstd.h"

namespace fs = std::filesystem;

const size_t SHARD_PIECE_SIZE = 2 * 1000 * 1000 * 1000;  // Roughly 2 gigabytes
const size_t COMPRESSION_BUFFER_SIZE = 4 * 1000 * 1000;  // Roughly 4 megabytes

std::vector<std::shared_ptr<::arrow::Field>> get_fields_for_file(
    arrow::MemoryPool* pool, const std::string& filename) {
    // Configure general Parquet reader settings
    auto reader_properties = parquet::ReaderProperties(pool);
    reader_properties.set_buffer_size(4096 * 4);
    reader_properties.enable_buffered_stream();

    // Configure Arrow-specific Parquet reader settings
    auto arrow_reader_props = parquet::ArrowReaderProperties();
    arrow_reader_props.set_batch_size(128 * 1024);  // default 64 * 1024

    parquet::arrow::FileReaderBuilder reader_builder;
    PARQUET_THROW_NOT_OK(reader_builder.OpenFile(filename, /*memory_map=*/false,
                                                 reader_properties));
    reader_builder.memory_pool(pool);
    reader_builder.properties(arrow_reader_props);

    std::unique_ptr<parquet::arrow::FileReader> arrow_reader;
    PARQUET_ASSIGN_OR_THROW(arrow_reader, reader_builder.Build());

    const auto& manifest = arrow_reader->manifest();

    std::vector<std::shared_ptr<::arrow::Field>> fields;

    for (const auto& schema_field : manifest.schema_fields) {
        if (schema_field.children.size() != 0 || !schema_field.is_leaf()) {
            throw std::runtime_error(
                "For MEDS-Flat fields should not be nested, but we have a "
                "non-nested field " +
                schema_field.field->name());
        }

        fields.push_back(schema_field.field);
    }

    return fields;
}

const std::vector<std::string> known_fields = {
    "patient_id",    "time",           "code",
    "numeric_value", "datetime_value", "text_value"};

std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>>
get_metadata_fields(const std::vector<std::string>& files) {
    arrow::MemoryPool* pool = arrow::default_memory_pool();
    std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>> result;

    for (const auto& file : files) {
        auto fields = get_fields_for_file(pool, file);
        for (const auto& field : fields) {
            if (field->name() == "value") {
                throw std::runtime_error(
                    "The C++ MEDS-Flat ETL does not currently support generic "
                    "value fields " +
                    field->ToString());
            }

            if (std::find(std::begin(known_fields), std::end(known_fields),
                          field->name()) == std::end(known_fields)) {
                result.insert(std::make_pair(field->name(), field->type()));
            }
        }
    }

    return result;
}

std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>>
get_metadata_fields_multithreaded(const std::vector<std::string>& files,
                                  size_t num_threads) {
    std::vector<std::thread> threads;
    std::vector<
        std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>>>
        results(num_threads);

    size_t files_per_thread = (files.size() + num_threads - 1) / num_threads;

    for (size_t i = 0; i < num_threads; i++) {
        threads.emplace_back([&files, i, &results, files_per_thread]() {
            std::vector<std::string> fraction;
            for (size_t j = files_per_thread * i;
                 j < std::min(files.size(), files_per_thread * (i + 1)); j++) {
                fraction.push_back(files[j]);
            }
            results[i] = get_metadata_fields(fraction);
        });
    }

    for (auto& thread : threads) {
        thread.join();
    }

    std::set<std::pair<std::string, std::shared_ptr<arrow::DataType>>> result;

    for (auto& res : results) {
        result.merge(std::move(res));
    }

    return result;
}

/*
struct Row {
    int64_t patient_id;

    int64_t time; // Actually an Arrow Timestamp with microsecond precision

    std::string code;

    absl::optional<float> numeric_value;
    absl::optional<int64_t> datetime_value; // Actually an Arrow Timestamp with
microsecond precision absl::optional<std::string> text_value;

    std::vector<absl::optional<std::string>> metadata_columns;
};

struct Row {
    int64_t patient_id;
    int64_t time;

    std::vector<char> data;

    bool operator<(const Row& rhs) {
        return std::make_pair(patient_id, time) <
               std::make_pair(rhs.patient_id, rhs.time);
    }
};
*/

template <typename T>
void add_literal_to_vector(std::vector<char>& data, T to_add) {
    const char* bytes = reinterpret_cast<const char*>(&to_add);
    data.insert(std::end(data), bytes, bytes + sizeof(T));
}

void add_string_to_vector(std::vector<char>& data, std::string_view to_add) {
    add_literal_to_vector(data, to_add.size());
    data.insert(std::end(data), std::begin(to_add), std::end(to_add));
}

using QueueItem = absl::optional<std::vector<char>>;

constexpr ssize_t SEMAPHORE_BLOCK_SIZE = 1000;

void shard_reader(
    size_t reader_index, size_t num_shards,
    moodycamel::BlockingConcurrentQueue<absl::optional<std::string>>&
        file_queue,
    std::vector<moodycamel::BlockingConcurrentQueue<QueueItem>>&
        all_write_queues,
    moodycamel::LightweightSemaphore& all_write_semaphore,
    const std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>&
        metadata_columns) {
    arrow::MemoryPool* pool = arrow::default_memory_pool();

    std::vector<moodycamel::ProducerToken> ptoks;
    for (size_t i = 0; i < num_shards; i++) {
        ptoks.emplace_back(all_write_queues[i]);
    }

    ssize_t slots_to_write = all_write_semaphore.waitMany(SEMAPHORE_BLOCK_SIZE);

    absl::optional<std::string> item;
    while (true) {
        file_queue.wait_dequeue(item);

        if (!item) {
            break;
        } else {
            auto source = *item;

            // Configure general Parquet reader settings
            auto reader_properties = parquet::ReaderProperties(pool);
            reader_properties.set_buffer_size(4096 * 4);
            reader_properties.enable_buffered_stream();

            // Configure Arrow-specific Parquet reader settings
            auto arrow_reader_props = parquet::ArrowReaderProperties();
            arrow_reader_props.set_batch_size(128 * 1024);  // default 64 * 1024

            parquet::arrow::FileReaderBuilder reader_builder;
            PARQUET_THROW_NOT_OK(reader_builder.OpenFile(
                source, /*memory_map=*/false, reader_properties));
            reader_builder.memory_pool(pool);
            reader_builder.properties(arrow_reader_props);

            std::unique_ptr<parquet::arrow::FileReader> arrow_reader;
            PARQUET_ASSIGN_OR_THROW(arrow_reader, reader_builder.Build());

            int patient_id_index = -1;
            int time_index = -1;
            int code_index = -1;

            int numeric_value_index = -1;
            int datetime_value_index = -1;
            int text_value_index = -1;

            std::vector<int> metadata_indices(metadata_columns.size(), -1);

            std::bitset<std::numeric_limits<unsigned long long>::digits>
                is_text_metadata;

            const auto& manifest = arrow_reader->manifest();
            for (const auto& schema_field : manifest.schema_fields) {
                if (schema_field.children.size() != 0 ||
                    !schema_field.is_leaf()) {
                    throw std::runtime_error(
                        "For MEDS-Flat fields should not be nested, but we "
                        "have a non-nested field " +
                        schema_field.field->name());
                }

                if (schema_field.field->name() == "patient_id") {
                    if (!schema_field.field->type()->Equals(
                            arrow::Int64Type())) {
                        throw std::runtime_error(
                            "C++ MEDS-Flat requires Int64 patient_ids but "
                            "found " +
                            schema_field.field->ToString());
                    }
                    patient_id_index = schema_field.column_index;
                } else if (schema_field.field->name() == "time") {
                    if (!schema_field.field->type()->Equals(
                            arrow::TimestampType(arrow::TimeUnit::MICRO))) {
                        throw std::runtime_error(
                            "C++ MEDS-Flat requires microsecond timestamp "
                            "times but found " +
                            schema_field.field->ToString());
                    }
                    time_index = schema_field.column_index;
                } else if (schema_field.field->name() == "code") {
                    if (!schema_field.field->type()->Equals(
                            arrow::LargeStringType())) {
                        throw std::runtime_error(
                            "The C++ MEDS-Flat ETL requires large_string codes "
                            "but found " +
                            schema_field.field->ToString());
                    }

                    code_index = schema_field.column_index;
                } else if (schema_field.field->name() == "numeric_value") {
                    if (!schema_field.field->type()->Equals(
                            arrow::FloatType())) {
                        throw std::runtime_error(
                            "C++ MEDS-Flat requires Float numeric_value but "
                            "found " +
                            schema_field.field->ToString());
                    }
                    numeric_value_index = schema_field.column_index;
                } else if (schema_field.field->name() == "datetime_value") {
                    if (!schema_field.field->type()->Equals(
                            arrow::TimestampType(arrow::TimeUnit::MICRO))) {
                        throw std::runtime_error(
                            "C++ MEDS-Flat requires microsecond timestamp "
                            "datetime_value but found " +
                            schema_field.field->ToString());
                    }
                    datetime_value_index = schema_field.column_index;
                } else if (schema_field.field->name() == "text_value") {
                    if (!schema_field.field->type()->Equals(
                            arrow::LargeStringType())) {
                        throw std::runtime_error(
                            "C++ MEDS-Flat requires Float32 numeric_value but "
                            "found " +
                            schema_field.field->ToString());
                    }
                    text_value_index = schema_field.column_index;
                } else {
                    // Must be metadata
                    auto iter = std::find_if(
                        std::begin(metadata_columns),
                        std::end(metadata_columns), [&](const auto& entry) {
                            return entry.first == schema_field.field->name();
                        });
                    if (iter == std::end(metadata_columns)) {
                        throw std::runtime_error(
                            "Had an extra column in the metadata that "
                            "shouldn't exist? " +
                            schema_field.field->ToString());
                    }

                    if (!schema_field.field->type()->Equals(iter->second)) {
                        throw std::runtime_error(
                            "C++ MEDS-Flat requires large_string metadata but "
                            "found " +
                            schema_field.field->ToString());
                    }

                    int offset = (iter - std::begin(metadata_columns));

                    if (iter->second->Equals(arrow::LargeStringType())) {
                        is_text_metadata[offset] = true;
                    } else {
                        is_text_metadata[offset] = false;

                        if (iter->second->byte_width() == -1) {
                            throw std::runtime_error(
                                "Found non text metadata with unknown byte "
                                "width? " +
                                iter->second->ToString());
                        }
                    }

                    metadata_indices[offset] = schema_field.column_index;
                }
            }

            if (patient_id_index == -1) {
                throw std::runtime_error(
                    "Could not find patient_id column index");
            }

            if (time_index == -1) {
                throw std::runtime_error("Could not find time column index");
            }

            if (code_index == -1) {
                throw std::runtime_error("Could not find code column index");
            }

            std::shared_ptr<::arrow::RecordBatchReader> rb_reader;
            PARQUET_THROW_NOT_OK(
                arrow_reader->GetRecordBatchReader(&rb_reader));

            std::shared_ptr<arrow::RecordBatch> record_batch;

            while (true) {
                PARQUET_THROW_NOT_OK(rb_reader->ReadNext(&record_batch));

                if (!record_batch) {
                    break;
                }

                auto patient_id_array = std::dynamic_pointer_cast<
                    arrow::NumericArray<arrow::Int64Type>>(
                    record_batch->column(patient_id_index));
                if (!patient_id_array) {
                    throw std::runtime_error("Could not cast patient_id array");
                }

                auto time_array = std::dynamic_pointer_cast<
                    arrow::NumericArray<arrow::TimestampType>>(
                    record_batch->column(time_index));
                if (!time_array) {
                    throw std::runtime_error("Could not cast time array");
                }

                auto code_array =
                    std::dynamic_pointer_cast<arrow::LargeStringArray>(
                        record_batch->column(code_index));
                if (!code_array) {
                    throw std::runtime_error("Could not cast code array");
                }

                auto numeric_value_array = std::dynamic_pointer_cast<
                    arrow::NumericArray<arrow::FloatType>>(
                    record_batch->column(numeric_value_index));
                if (!numeric_value_array) {
                    throw std::runtime_error(
                        "Could not cast numeric_value array");
                }

                auto datetime_value_array = std::dynamic_pointer_cast<
                    arrow::NumericArray<arrow::TimestampType>>(
                    record_batch->column(datetime_value_index));
                if (!datetime_value_array) {
                    throw std::runtime_error(
                        "Could not cast datetime_value array");
                }

                auto text_value_array =
                    std::dynamic_pointer_cast<arrow::LargeStringArray>(
                        record_batch->column(text_value_index));
                if (!text_value_array) {
                    throw std::runtime_error("Could not cast text_value array");
                }

                std::vector<std::shared_ptr<arrow::LargeStringArray>>
                    text_metadata_arrays(metadata_columns.size());
                std::vector<std::shared_ptr<arrow::FixedSizeBinaryArray>>
                    primitive_metadata_arrays(metadata_columns.size());

                for (size_t i = 0; i < metadata_columns.size(); i++) {
                    if (metadata_indices[i] == -1) {
                        continue;
                    }

                    if (is_text_metadata[i]) {
                        auto metadata_array =
                            std::dynamic_pointer_cast<arrow::LargeStringArray>(
                                record_batch->column(metadata_indices[i]));
                        if (!metadata_array) {
                            throw std::runtime_error(
                                "Could not cast metadata array to text" +
                                metadata_columns[i].first + " " +
                                metadata_columns[i].second->ToString());
                        }
                        text_metadata_arrays[i] = metadata_array;
                    } else {
                        std::shared_ptr<arrow::Array> fixed_size_array;
                        PARQUET_ASSIGN_OR_THROW(
                            fixed_size_array,
                            record_batch->column(metadata_indices[i])
                                ->View(std::make_shared<
                                       arrow::FixedSizeBinaryType>(
                                    metadata_columns[i].second->byte_width())));

                        auto metadata_array = std::dynamic_pointer_cast<
                            arrow::FixedSizeBinaryArray>(fixed_size_array);
                        if (!metadata_array) {
                            throw std::runtime_error(
                                "Could not cast metadata array to fixed size " +
                                metadata_columns[i].first + " " +
                                metadata_columns[i].second->ToString());
                        }
                        primitive_metadata_arrays[i] = metadata_array;
                    }
                }

                for (int64_t i = 0; i < text_value_array->length(); i++) {
                    if (!patient_id_array->IsValid(i)) {
                        throw std::runtime_error(
                            "patient_id incorrectly has null value " + source);
                    }
                    if (!time_array->IsValid(i)) {
                        throw std::runtime_error(
                            "time incorrectly has null value " + source);
                    }
                    if (!code_array->IsValid(i)) {
                        throw std::runtime_error(
                            "code incorrectly has null value " + source);
                    }

                    std::vector<char> data;

                    int64_t patient_id = patient_id_array->Value(i);
                    int64_t time = time_array->Value(i);

                    std::bitset<std::numeric_limits<unsigned long long>::digits>
                        non_null;

                    add_literal_to_vector(data, patient_id);
                    add_literal_to_vector(data, time);

                    add_string_to_vector(data, code_array->Value(i));

                    if (numeric_value_array->IsValid(i)) {
                        non_null[0] = true;
                        add_literal_to_vector(data,
                                              numeric_value_array->Value(i));
                    }

                    if (datetime_value_array->IsValid(i)) {
                        non_null[1] = true;
                        add_literal_to_vector(data,
                                              datetime_value_array->Value(i));
                    }

                    if (text_value_array->IsValid(i)) {
                        non_null[2] = true;
                        add_string_to_vector(data, text_value_array->Value(i));
                    }

                    for (size_t j = 0; j < metadata_columns.size(); j++) {
                        if (is_text_metadata[j]) {
                            if (text_metadata_arrays[j] &&
                                text_metadata_arrays[j]->IsValid(i)) {
                                non_null[3 + j] = true;
                                add_string_to_vector(
                                    data, text_metadata_arrays[j]->Value(i));
                            }
                        } else {
                            if (primitive_metadata_arrays[j] &&
                                primitive_metadata_arrays[j]->IsValid(i)) {
                                non_null[3 + j] = true;
                                add_string_to_vector(
                                    data,
                                    primitive_metadata_arrays[j]->GetView(i));
                            }
                        }
                    }

                    add_literal_to_vector(data, non_null.to_ullong());

                    size_t index =
                        std::hash<int64_t>()(patient_id) % num_shards;
                    all_write_queues[index].enqueue(ptoks[index],
                                                    std::move(data));

                    slots_to_write--;
                    if (slots_to_write == 0) {
                        slots_to_write =
                            all_write_semaphore.waitMany(SEMAPHORE_BLOCK_SIZE);
                    }
                }
            }
        }
    }

    for (size_t j = 0; j < num_shards; j++) {
        all_write_queues[j].enqueue(ptoks[j], absl::nullopt);
    }

    if (slots_to_write > 0) {
        all_write_semaphore.signal(slots_to_write);
    }
}

class ZstdRowWriter {
   public:
    ZstdRowWriter(const std::string& path, ZSTD_CCtx* ctx)
        : fname(path),
          fstream(path, std::ifstream::out | std::ifstream::binary),
          context(ctx) {}

    void add_next(std::string_view data) {
        add_string_to_vector(uncompressed_buffer,
                             std::string_view(data.data(), data.size()));

        if (uncompressed_buffer.size() > COMPRESSION_BUFFER_SIZE) {
            flush_compressed();
        }
    }

    ~ZstdRowWriter() {
        if (uncompressed_buffer.size() > 0) {
            flush_compressed();
        }
    }

    const std::string fname;

   private:
    void flush_compressed() {
        size_t needed_size = ZSTD_compressBound(uncompressed_buffer.size());

        if (compressed_buffer.size() < needed_size) {
            compressed_buffer.resize(needed_size * 2);
        }

        size_t compressed_length = ZSTD_compressCCtx(
            context, compressed_buffer.data(), compressed_buffer.size(),
            uncompressed_buffer.data(), uncompressed_buffer.size(), 1);

        if (ZSTD_isError(compressed_length)) {
            throw std::runtime_error("Could not compress using zstd?");
        }

        fstream.write(reinterpret_cast<char*>(&compressed_length),
                      sizeof(compressed_length));
        fstream.write(compressed_buffer.data(), compressed_length);

        uncompressed_buffer.clear();
    }

    std::ofstream fstream;

    ZSTD_CCtx* context;

    std::vector<char> compressed_buffer;
    std::vector<char> uncompressed_buffer;
};

class ZstdRowReader {
   public:
    ZstdRowReader(const std::string& path, ZSTD_DCtx* ctx)
        : fname(path),
          fstream(path, std::ifstream::in | std::ifstream::binary),
          context(ctx),
          current_offset(0),
          uncompressed_size(0) {}

    absl::optional<std::tuple<int64_t, int64_t, std::string_view>> get_next() {
        if (current_offset == uncompressed_size) {
            bool could_load_more = try_to_load_more_data();

            if (!could_load_more) {
                return {};
            }

            assert(current_offset < uncompressed_size);
        }

        assert(compressed_buffer.size() >= sizeof(size_t));

        size_t size = *reinterpret_cast<const size_t*>(
            uncompressed_buffer.data() + current_offset);
        current_offset += sizeof(size);

        std::string_view data(uncompressed_buffer.data() + current_offset,
                              size);
        current_offset += size;

        assert(data.size() >= sizeof(int64_t) * 2);
        assert(data.data() != nullptr);

        int64_t patient_id = *reinterpret_cast<const int64_t*>(data.data() + 0);
        int64_t time =
            *reinterpret_cast<const int64_t*>(data.data() + sizeof(int64_t));

        return std::make_tuple(patient_id, time, data);
    }

   private:
    bool try_to_load_more_data() {
        if (fstream.eof()) {
            return false;
        }

        size_t size;
        fstream.read(reinterpret_cast<char*>(&size), sizeof(size));

        if (fstream.eof()) {
            return false;
        }

        if (compressed_buffer.size() < size) {
            compressed_buffer.resize(size * 2);
        }

        fstream.read(compressed_buffer.data(), size);

        uncompressed_size =
            ZSTD_getFrameContentSize(compressed_buffer.data(), size);

        if (uncompressed_size == ZSTD_CONTENTSIZE_ERROR ||
            uncompressed_size == ZSTD_CONTENTSIZE_UNKNOWN) {
            throw std::runtime_error(
                "Could not get the size of the zstd compressed stream?");
        }

        if (uncompressed_buffer.size() < uncompressed_size) {
            uncompressed_buffer.resize(uncompressed_size * 2);
        }

        size_t read_size = ZSTD_decompressDCtx(
            context, uncompressed_buffer.data(), uncompressed_size,
            compressed_buffer.data(), size);

        if (ZSTD_isError(read_size) || read_size != uncompressed_size) {
            throw std::runtime_error("Could not decompress zstd data?");
        }

        current_offset = 0;
        return true;
    }

    const std::string fname;
    std::ifstream fstream;

    ZSTD_DCtx* context;

    std::vector<char> compressed_buffer;
    std::vector<char> uncompressed_buffer;
    size_t current_offset;
    size_t uncompressed_size;
};

void shard_writer(
    size_t writer_index, size_t num_shards,
    moodycamel::BlockingConcurrentQueue<QueueItem>& write_queue,
    moodycamel::LightweightSemaphore& write_semaphore,
    const std::filesystem::path& target_dir,
    moodycamel::BlockingConcurrentQueue<std::string>& sort_file_queue,
    std::atomic<ssize_t>& remaining_live_writers) {
    std::filesystem::create_directory(target_dir);

    size_t current_size = 0;

    size_t current_file_index = 0;

    auto context_deleter = [](ZSTD_CCtx* context) { ZSTD_freeCCtx(context); };

    std::unique_ptr<ZSTD_CCtx, decltype(context_deleter)> context{
        ZSTD_createCCtx(), context_deleter};

    std::optional<ZstdRowWriter> current_writer;

    auto init_file = [&]() {
        auto target_file = target_dir / std::to_string(current_file_index);
        current_writer.emplace(target_file, context.get());
    };

    auto flush_file = [&]() {
        std::string target_file = current_writer->fname;
        current_writer.reset();

        sort_file_queue.enqueue(target_file);

        current_size = 0;
        current_file_index += 1;
    };

    QueueItem item;
    size_t readers_remaining = num_shards;

    moodycamel::ConsumerToken ctok(write_queue);

    size_t num_read = 0;

    while (true) {
        write_queue.wait_dequeue(ctok, item);

        if (!item) {
            readers_remaining--;
            if (readers_remaining == 0) {
                break;
            } else {
                continue;
            }
        }

        num_read++;
        if (num_read == SEMAPHORE_BLOCK_SIZE) {
            write_semaphore.signal(num_read);
            num_read = 0;
        }

        std::vector<char>& r = *item;

        if (!current_writer) {
            init_file();
        }

        current_writer->add_next(std::string_view(r.data(), r.size()));

        current_size += sizeof(size_t) + r.size();

        if (current_size > SHARD_PIECE_SIZE) {
            flush_file();
        }
    }

    write_semaphore.signal(num_read);

    if (current_writer) {
        flush_file();
    }

    remaining_live_writers.fetch_sub(1, std::memory_order_release);
}

void shard_sort(
    moodycamel::BlockingConcurrentQueue<std::string>& sort_file_queue,
    const std::atomic<ssize_t>& remaining_live_writers) {
    absl::optional<std::string> next_entry;

    std::vector<char> data;
    std::vector<std::tuple<int64_t, int64_t, size_t, size_t>> row_indices;

    auto compression_context_deleter = [](ZSTD_CCtx* context) {
        ZSTD_freeCCtx(context);
    };
    auto decompression_context_deleter = [](ZSTD_DCtx* context) {
        ZSTD_freeDCtx(context);
    };

    std::unique_ptr<ZSTD_CCtx, decltype(compression_context_deleter)>
        compression_context{ZSTD_createCCtx(), compression_context_deleter};

    std::unique_ptr<ZSTD_DCtx, decltype(decompression_context_deleter)>
        decompression_context{ZSTD_createDCtx(), decompression_context_deleter};

    std::string filename;
    while (true) {
        while (true) {
            bool found = sort_file_queue.wait_dequeue_timed(filename, 1e6);
            if (found) {
                break;
            }

            // No items are available. This could be due to being fully done.

            // Check if we are done
            if (remaining_live_writers.load(std::memory_order_acquire) == 0) {
                return;
            }

            // Need to wait more
        }

        data.clear();
        row_indices.clear();

        {
            ZstdRowReader reader(filename, decompression_context.get());

            while (true) {
                auto next = reader.get_next();

                if (!next) {
                    break;
                }

                size_t start = data.size();
                size_t length = std::get<2>(*next).size();

                data.insert(std::end(data), std::begin(std::get<2>(*next)),
                            std::end(std::get<2>(*next)));
                row_indices.push_back(std::make_tuple(
                    std::get<0>(*next), std::get<1>(*next), start, length));
            }
        }

        std::sort(std::begin(row_indices), std::end(row_indices));

        {
            ZstdRowWriter writer(filename, compression_context.get());

            for (const auto& row_index : row_indices) {
                writer.add_next(
                    std::string_view(data.data() + std::get<2>(row_index),
                                     std::get<3>(row_index)));
            }
        }
    }
}

constexpr int QUEUE_SIZE = 10000;

std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>
sort_and_shard(const std::filesystem::path& source_directory,
               const std::filesystem::path& target_directory,
               size_t num_shards) {
    std::filesystem::create_directory(target_directory);

    std::vector<std::string> paths;

    for (const auto& entry : fs::directory_iterator(source_directory)) {
        paths.push_back(entry.path());
    }

    auto set_metadata_fields =
        get_metadata_fields_multithreaded(paths, num_shards);

    std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>
        metadata_columns(std::begin(set_metadata_fields),
                         std::end(set_metadata_fields));
    std::sort(std::begin(metadata_columns), std::end(metadata_columns));

    metadata_columns.erase(
        std::unique(std::begin(metadata_columns), std::end(metadata_columns),
                    [](const auto& a, const auto& b) {
                        return (a.first == b.first) &&
                               a.second->Equals(b.second);
                    }),
        std::end(metadata_columns));

    for (ssize_t i = 0; i < static_cast<ssize_t>(metadata_columns.size()) - 1;
         i++) {
        if (metadata_columns[i].first == metadata_columns[i + 1].first) {
            throw std::runtime_error(
                "Got conflicting types for column " +
                metadata_columns[i].first +
                ", types: " + metadata_columns[i].second->ToString() + " vs " +
                metadata_columns[i + 1].second->ToString());
        }
    }

    if (metadata_columns.size() + 3 >
        std::numeric_limits<unsigned long long>::digits) {
        throw std::runtime_error(
            "C++ MEDS-ETL currently only supports at most " +
            std::to_string(std::numeric_limits<unsigned long long>::digits) +
            " metadata columns");
    }

    moodycamel::BlockingConcurrentQueue<absl::optional<std::string>> file_queue;

    for (const auto& path : paths) {
        file_queue.enqueue(path);
    }

    for (size_t i = 0; i < num_shards; i++) {
        file_queue.enqueue({});
    }

    std::vector<moodycamel::BlockingConcurrentQueue<QueueItem>> write_queues(
        num_shards);

    std::vector<std::thread> threads;

    moodycamel::LightweightSemaphore write_semaphore(QUEUE_SIZE * num_shards);

    moodycamel::BlockingConcurrentQueue<std::string> sort_queue;
    std::atomic<ssize_t> remaining_live_writers(num_shards);

    for (size_t i = 0; i < num_shards; i++) {
        threads.emplace_back([i, &file_queue, &write_queues, &write_semaphore,
                              num_shards, &metadata_columns]() {
            shard_reader(i, num_shards, file_queue, write_queues,
                         write_semaphore, metadata_columns);
        });

        threads.emplace_back([i, &write_queues, &write_semaphore, num_shards,
                              target_directory, &sort_queue,
                              &remaining_live_writers]() {
            shard_writer(i, num_shards, write_queues[i], write_semaphore,
                         target_directory / std::to_string(i), sort_queue,
                         remaining_live_writers);
        });

        threads.emplace_back([&sort_queue, &remaining_live_writers]() {
            shard_sort(sort_queue, remaining_live_writers);
        });
    }

    for (auto& thread : threads) {
        thread.join();
    }

    absl::optional<std::string> next_entry;
    if (sort_queue.try_dequeue(next_entry)) {
        // This should not be possible
        throw std::runtime_error(
            "Had excess unsorted items. This should not be possible");
    }

    return metadata_columns;
}

void join_and_write_single(
    const std::filesystem::path& source_directory,
    const std::filesystem::path& target_path,
    const std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>&
        metadata_columns) {
    arrow::FieldVector metadata_fields;
    std::bitset<std::numeric_limits<unsigned long long>::digits>
        is_text_metadata;
    for (size_t i = 0; i < metadata_columns.size(); i++) {
        const auto& metadata_column = metadata_columns[i];
        if (metadata_column.second->Equals(arrow::LargeStringType())) {
            is_text_metadata[i] = true;
            metadata_fields.push_back(arrow::field(
                metadata_column.first, std::make_shared<arrow::StringType>()));
        } else {
            is_text_metadata[i] = false;
            metadata_fields.push_back(
                arrow::field(metadata_column.first, metadata_column.second));
        }
    }

    auto metadata_type = std::make_shared<arrow::StructType>(metadata_fields);

    auto timestamp_type =
        std::make_shared<arrow::TimestampType>(arrow::TimeUnit::MICRO);

    auto measurement_type_fields = {
        arrow::field("code", std::make_shared<arrow::StringType>()),

        arrow::field("text_value", std::make_shared<arrow::StringType>()),
        arrow::field("numeric_value", std::make_shared<arrow::FloatType>()),
        arrow::field("datetime_value", std::make_shared<arrow::TimestampType>(
                                           arrow::TimeUnit::MICRO)),

        arrow::field("metadata", metadata_type),
    };
    auto measurement_type =
        std::make_shared<arrow::StructType>(measurement_type_fields);

    auto event_type_fields = {
        arrow::field("time", std::make_shared<arrow::TimestampType>(
                                 arrow::TimeUnit::MICRO)),
        arrow::field("measurements",
                     std::make_shared<arrow::ListType>(measurement_type)),
    };
    auto event_type = std::make_shared<arrow::StructType>(event_type_fields);
    auto events_type = std::make_shared<arrow::ListType>(event_type);

    auto schema_fields = {
        arrow::field("patient_id", std::make_shared<arrow::Int64Type>()),
        arrow::field("static_measurements",
                     std::make_shared<arrow::NullType>()),
        arrow::field("events", events_type),
    };
    auto schema = std::make_shared<arrow::Schema>(schema_fields);

    using parquet::ArrowWriterProperties;
    using parquet::WriterProperties;

    size_t amount_written = 0;

    arrow::MemoryPool* pool = arrow::default_memory_pool();

    // Choose compression
    std::shared_ptr<WriterProperties> props =
        WriterProperties::Builder()
            .compression(arrow::Compression::ZSTD)
            ->build();

    // Opt to store Arrow schema for easier reads back into Arrow
    std::shared_ptr<ArrowWriterProperties> arrow_props =
        ArrowWriterProperties::Builder().store_schema()->build();

    // Create a writer
    std::shared_ptr<arrow::io::FileOutputStream> outfile;
    PARQUET_ASSIGN_OR_THROW(
        outfile, arrow::io::FileOutputStream::Open(target_path.string()));
    std::unique_ptr<parquet::arrow::FileWriter> writer;
    PARQUET_ASSIGN_OR_THROW(
        writer, parquet::arrow::FileWriter::Open(*schema, pool, outfile, props,
                                                 arrow_props));

    std::vector<ZstdRowReader> source_files;

    auto context_deleter = [](ZSTD_DCtx* context) { ZSTD_freeDCtx(context); };

    std::unique_ptr<ZSTD_DCtx, decltype(context_deleter)> context{
        ZSTD_createDCtx(), context_deleter};

    for (const auto& entry : fs::directory_iterator(source_directory)) {
        source_files.emplace_back(entry.path(), context.get());
    }

    typedef std::tuple<int64_t, int64_t, size_t, std::string_view>
        PriorityQueueItem;

    std::priority_queue<PriorityQueueItem, std::vector<PriorityQueueItem>,
                        std::greater<PriorityQueueItem>>
        queue;

    for (size_t i = 0; i < source_files.size(); i++) {
        auto next_entry = source_files[i].get_next();
        if (!next_entry) {
            continue;
        }

        queue.push(std::make_tuple(std::get<0>(*next_entry),
                                   std::get<1>(*next_entry), i,
                                   std::get<2>(*next_entry)));
    }

    auto patient_id_builder = std::make_shared<arrow::Int64Builder>(pool);
    auto static_measurements_builder =
        std::make_shared<arrow::NullBuilder>(pool);

    auto code_builder = std::make_shared<arrow::StringBuilder>(pool);

    auto text_value_builder = std::make_shared<arrow::StringBuilder>(pool);
    auto numeric_value_builder = std::make_shared<arrow::FloatBuilder>(pool);
    auto datetime_value_builder =
        std::make_shared<arrow::TimestampBuilder>(timestamp_type, pool);

    std::vector<std::shared_ptr<arrow::StringBuilder>> text_metadata_builders(
        metadata_columns.size());
    std::vector<std::shared_ptr<arrow::FixedSizeBinaryBuilder>>
        primitive_metadata_builders(metadata_columns.size());
    std::vector<std::shared_ptr<arrow::ArrayBuilder>> metadata_builders(
        metadata_columns.size());
    for (size_t i = 0; i < metadata_columns.size(); i++) {
        if (is_text_metadata[i]) {
            auto builder = std::make_shared<arrow::StringBuilder>(pool);
            text_metadata_builders[i] = builder;
            metadata_builders[i] = builder;
        } else {
            auto builder = std::make_shared<arrow::FixedSizeBinaryBuilder>(
                std::make_shared<arrow::FixedSizeBinaryType>(
                    metadata_columns[i].second->byte_width()));
            primitive_metadata_builders[i] = builder;
            metadata_builders[i] = builder;
        }
    }

    auto metadata_builder = std::make_shared<arrow::StructBuilder>(
        metadata_type, pool, metadata_builders);

    std::vector<std::shared_ptr<arrow::ArrayBuilder>>
        measurement_builder_fields{code_builder, text_value_builder,
                                   numeric_value_builder,
                                   datetime_value_builder, metadata_builder};
    auto measurement_builder = std::make_shared<arrow::StructBuilder>(
        measurement_type, pool, measurement_builder_fields);

    auto time_builder =
        std::make_shared<arrow::TimestampBuilder>(timestamp_type, pool);
    auto measurements_builder =
        std::make_shared<arrow::ListBuilder>(pool, measurement_builder);

    std::vector<std::shared_ptr<arrow::ArrayBuilder>> event_builder_fields{
        time_builder, measurements_builder};
    auto event_builder = std::make_shared<arrow::StructBuilder>(
        event_type, pool, event_builder_fields);

    auto events_builder =
        std::make_shared<arrow::ListBuilder>(pool, event_builder);

    auto flush_arrays = [&]() {
        std::vector<std::shared_ptr<arrow::Array>> columns(3);
        PARQUET_THROW_NOT_OK(patient_id_builder->Finish(columns.data() + 0));
        PARQUET_THROW_NOT_OK(
            static_measurements_builder->Finish(columns.data() + 1));

        std::shared_ptr<arrow::Array> events_array;
        PARQUET_THROW_NOT_OK(events_builder->Finish(&events_array));
        PARQUET_ASSIGN_OR_THROW(columns[2], events_array->View(events_type));

        std::shared_ptr<arrow::Table> table =
            arrow::Table::Make(schema, columns);
        PARQUET_THROW_NOT_OK(writer->WriteTable(*table));

        amount_written = 0;
    };

    bool is_first = true;
    int64_t last_patient_id = -1;
    int64_t last_time = -1;

    while (!queue.empty()) {
        auto next = std::move(queue.top());
        queue.pop();

        int64_t patient_id = std::get<0>(next);
        int64_t time = std::get<1>(next);
        std::string_view patient_record = std::get<3>(next);
        amount_written += patient_record.size();

        if (patient_id != last_patient_id || is_first) {
            is_first = false;

            if (amount_written > SHARD_PIECE_SIZE) {
                flush_arrays();
            }

            last_patient_id = patient_id;
            last_time = time;

            PARQUET_THROW_NOT_OK(patient_id_builder->Append(patient_id));
            PARQUET_THROW_NOT_OK(static_measurements_builder->AppendNull());
            PARQUET_THROW_NOT_OK(events_builder->Append());

            PARQUET_THROW_NOT_OK(event_builder->Append());
            PARQUET_THROW_NOT_OK(time_builder->Append(time));
            PARQUET_THROW_NOT_OK(measurements_builder->Append());
        } else if (time != last_time) {
            last_time = time;

            PARQUET_THROW_NOT_OK(event_builder->Append());
            PARQUET_THROW_NOT_OK(time_builder->Append(time));
            PARQUET_THROW_NOT_OK(measurements_builder->Append());
        }

        PARQUET_THROW_NOT_OK(measurement_builder->Append());
        std::bitset<std::numeric_limits<unsigned long long>::digits> non_null(
            *reinterpret_cast<const unsigned long long*>(
                patient_record.data() + patient_record.size() -
                sizeof(unsigned long long)));
        size_t offset = sizeof(int64_t) * 2;

        size_t size = *reinterpret_cast<const size_t*>(
            patient_record.substr(offset).data());
        offset += sizeof(size);
        PARQUET_THROW_NOT_OK(
            code_builder->Append(patient_record.substr(offset, size)));
        offset += size;

        if (non_null[0]) {
            PARQUET_THROW_NOT_OK(
                numeric_value_builder->Append(*reinterpret_cast<const float*>(
                    patient_record.substr(offset).data())));
            offset += sizeof(float);
        } else {
            PARQUET_THROW_NOT_OK(numeric_value_builder->AppendNull());
        }

        if (non_null[1]) {
            PARQUET_THROW_NOT_OK(datetime_value_builder->Append(
                *reinterpret_cast<const int64_t*>(
                    patient_record.substr(offset).data())));
            offset += sizeof(int64_t);
        } else {
            PARQUET_THROW_NOT_OK(datetime_value_builder->AppendNull());
        }

        if (non_null[2]) {
            size_t size = *reinterpret_cast<const size_t*>(
                patient_record.substr(offset).data());
            offset += sizeof(size);
            PARQUET_THROW_NOT_OK(text_value_builder->Append(
                patient_record.substr(offset, size)));
            offset += size;
        } else {
            PARQUET_THROW_NOT_OK(text_value_builder->AppendNull());
        }

        PARQUET_THROW_NOT_OK(metadata_builder->Append());
        for (size_t j = 0; j < metadata_columns.size(); j++) {
            if (non_null[3 + j]) {
                size_t size = *reinterpret_cast<const size_t*>(
                    patient_record.substr(offset).data());
                offset += sizeof(size);
                auto entry = patient_record.substr(offset, size);

                if (is_text_metadata[j]) {
                    PARQUET_THROW_NOT_OK(
                        text_metadata_builders[j]->Append(entry));
                } else {
                    PARQUET_THROW_NOT_OK(
                        primitive_metadata_builders[j]->Append(entry));
                }
                offset += size;
            } else {
                if (is_text_metadata[j]) {
                    PARQUET_THROW_NOT_OK(
                        text_metadata_builders[j]->AppendNull());
                } else {
                    PARQUET_THROW_NOT_OK(
                        primitive_metadata_builders[j]->AppendNull());
                }
            }
        }

        size_t file_index = std::get<2>(next);
        auto next_entry = source_files[file_index].get_next();
        if (!next_entry) {
            continue;
        }

        queue.push(std::make_tuple(std::get<0>(*next_entry),
                                   std::get<1>(*next_entry), file_index,
                                   std::get<2>(*next_entry)));
    }

    flush_arrays();

    // Write file footer and close
    PARQUET_THROW_NOT_OK(writer->Close());
}

void join_and_write(
    const std::filesystem::path& source_directory,
    const std::filesystem::path& target_directory,
    const std::vector<std::pair<std::string, std::shared_ptr<arrow::DataType>>>&
        metadata_columns) {
    std::filesystem::create_directory(target_directory);

    std::vector<std::string> shards;

    for (const auto& entry : fs::directory_iterator(source_directory)) {
        shards.push_back(fs::relative(entry.path(), source_directory));
    }

    std::vector<std::thread> threads;

    for (const auto& shard : shards) {
        threads.emplace_back(
            [shard, &source_directory, &target_directory, &metadata_columns]() {
                join_and_write_single(source_directory / shard,
                                      target_directory / (shard + ".parquet"),
                                      metadata_columns);
            });
    }

    for (auto& thread : threads) {
        thread.join();
    }
}

void perform_etl(const std::string& source_directory,
                 const std::string& target_directory, size_t num_shards) {
    std::filesystem::path source_path(source_directory);
    std::filesystem::path target_path(target_directory);

    std::filesystem::create_directory(target_path);

    if (fs::exists(source_path / "metadata.json")) {
        fs::copy_file(source_path / "metadata.json",
                      target_path / "metadata.json");
    }

    std::filesystem::path shard_path = target_path / "shards";
    std::filesystem::path data_path = target_path / "data";

    auto metadata_columns =
        sort_and_shard(source_path / "flat_data", shard_path, num_shards);
    join_and_write(shard_path, data_path, metadata_columns);

    fs::remove_all(shard_path);
}
