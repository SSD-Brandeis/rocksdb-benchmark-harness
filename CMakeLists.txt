cmake_minimum_required(VERSION 3.16)
project(rocksdb-benchmark-harness)

set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_subdirectory(vendor/rocksdb)


add_executable(rocksdb-benchmark-harness src/main.cc)
target_link_libraries(rocksdb-benchmark-harness PUBLIC rocksdb)
target_include_directories(rocksdb-benchmark-harness PUBLIC
    "${PROJECT_BINARY_DIR}"
    "${PROJECT_SOURCE_DIR}/vendor/rocksdb/include/rocksdb"
)

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    set(WITH_UBSAN ON)
    target_compile_options(rocksdb-benchmark-harness PUBLIC -fsanitize=address,undefined)
    target_link_options(rocksdb-benchmark-harness PUBLIC -fsanitize=address,undefined)
endif()

