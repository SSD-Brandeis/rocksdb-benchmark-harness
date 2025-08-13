cmake_minimum_required(VERSION 3.16)
project(rocksdb-benchmark-harness)

include(FetchContent)

FetchContent_Declare(
        fmt
        GIT_REPOSITORY https://github.com/fmtlib/fmt
        GIT_TAG        11.2.0)
FetchContent_MakeAvailable(fmt)

FetchContent_Declare(
        json
        URL https://github.com/nlohmann/json/releases/download/v3.12.0/json.tar.xz
        DOWNLOAD_EXTRACT_TIMESTAMP TRUE)
FetchContent_MakeAvailable(json)


set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
add_subdirectory(vendor/rocksdb)

#option(TIMER "Enable operation timings" OFF)
#if(TIMER)
#  add_compile_definitions(TIMER)
#endif()

add_executable(rocksdb-benchmark-harness src/main.cc)
target_link_libraries(rocksdb-benchmark-harness PUBLIC rocksdb)
target_link_libraries(rocksdb-benchmark-harness PRIVATE fmt::fmt)
target_link_libraries(rocksdb-benchmark-harness PRIVATE nlohmann_json::nlohmann_json)
target_include_directories(rocksdb-benchmark-harness PUBLIC
    "${PROJECT_BINARY_DIR}"
    "${PROJECT_SOURCE_DIR}/vendor/rocksdb/include/rocksdb"
)

if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  set(WITH_UBSAN ON)
  target_compile_options(rocksdb-benchmark-harness PUBLIC -fsanitize=address,undefined)
  target_link_options(rocksdb-benchmark-harness PUBLIC -fsanitize=address,undefined)
endif()

