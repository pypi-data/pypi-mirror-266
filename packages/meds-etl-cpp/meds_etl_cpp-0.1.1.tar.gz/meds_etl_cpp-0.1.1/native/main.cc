#include "perform_etl.hh"

int main() {
    size_t num_shards = 2;

    std::string path_to_folder =
        "/labs/shahlab/projects/ethanid/mimic_test/mimic_demo/temp";
    std::string output =
        "/labs/shahlab/projects/ethanid/optimize_etl/meds_etl_cpp/native/"
        "output";

    perform_etl(path_to_folder, output, num_shards);
}
