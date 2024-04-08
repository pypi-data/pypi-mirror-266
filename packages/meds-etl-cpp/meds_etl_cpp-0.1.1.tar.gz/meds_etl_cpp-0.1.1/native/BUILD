load(
    "@rules_foreign_cc//foreign_cc:defs.bzl", "cmake", "configure_make", "make"
)

load("@pybind11_bazel//:build_defs.bzl", "pybind_library", "pybind_extension")

cc_binary(
    name="simple_test",
    srcs=["simple_test.cc"],
)

cc_library(
    name="perform_etl",
    srcs=["perform_etl.cc"],
    hdrs=["perform_etl.hh"],
    deps=[
        ":arrow", 
        "@com_google_absl//absl/types:optional",
        "@readerwriterqueue",
        "@concurrentqueue",
        ":zstd",
    ],
)

cc_binary(
    name="main",
    srcs=["main.cc"],
    deps=[
        ":perform_etl", 
    ],
)

pybind_extension(
    name="meds_etl_cpp",
    srcs=[
        "meds_etl_cpp.cc",
    ],
    deps=[":perform_etl"],
)

cmake(
    name = "arrow",
    build_args = [
        "-j `nproc`",
    ],
    cache_entries = {
        "CMAKE_C_FLAGS": "-fPIC -I/usr/include",
        "CMAKE_CXX_FLAGS": "-fPIC -I/usr/include",
        "ARROW_BUILD_SHARED": "OFF",
        "ARROW_BUILD_STATIC": "ON",
        "ARROW_BUILD_TESTS": "OFF",
        "ARROW_PARQUET": "ON",
        "ARROW_WITH_SNAPPY": "ON",
        "ARROW_WITH_ZSTD": "ON",
        "EP_COMMON_CMAKE_ARGS": "-DWITH_OPENSSL=OFF",
        "ARROW_DEPENDENCY_SOURCE": "BUNDLED",
    },
    tags = ["requires-network"],
    generate_args = ["-DCMAKE_RANLIB=/usr/bin/ranlib"],
    working_directory="cpp",
    lib_source = "@arrow//:all",
    out_lib_dir = "lib64",
    out_static_libs = ["libparquet.a", "libarrow.a", "libarrow_bundled_dependencies.a"],
    linkopts = ["-pthread"],
)

cmake(
    name = "zstd",
    cache_entries = {
        "CMAKE_C_FLAGS": "-fPIC",
        "CMAKE_CXX_FLAGS": "-fPIC",
    },
    working_directory="build/cmake",
    lib_source = "@zstd//:all",
    out_lib_dir = "lib64",
    out_static_libs = ["libzstd.a"],
)