#include "convenience.h"
#include "rocksdb/db.h"
#include "utilities/options_util.h"

#include <cstdlib>
#include <fstream>
#include <memory>
#include <fmt/base.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
using hrc = std::chrono::high_resolution_clock;
using ns = std::chrono::nanoseconds;


std::tuple<rocksdb::Status, rocksdb::Options, rocksdb::ReadOptions, rocksdb::WriteOptions> load_options(
  const std::string &filename
) {
  rocksdb::DBOptions db_opts;
  std::vector<rocksdb::ColumnFamilyDescriptor> cf_descs;

  rocksdb::Status s = rocksdb::LoadOptionsFromFile(
    rocksdb::ConfigOptions(),
    filename,
    &db_opts,
    &cf_descs
  );
  if (!s.ok()) {
    return {s, rocksdb::Options(), rocksdb::ReadOptions(), rocksdb::WriteOptions()};
  }

  const rocksdb::Options options(db_opts, cf_descs[0].options);

  rocksdb::ReadOptions read_options;
  rocksdb::WriteOptions write_options;

  return {rocksdb::Status::OK(), options, read_options, write_options};
}


#define FAIL(msg, status)      \
  do {                         \
    fmt::println(              \
      stderr,                  \
      "{}:{} {} {}",           \
      __FILE__,                \
      __LINE__,                \
      msg,                     \
      (status).ToString()      \
    );                         \
    exit(EXIT_FAILURE);        \
  } while (0)

namespace stats {
  enum Operation {
    Insert,
    Update,
    Merge,
    PointDelete,
    RangeDelete,
    PointQuery,
    RangeQuery,
  };

  NLOHMANN_JSON_SERIALIZE_ENUM(Operation, {
                               {Insert, "Insert"},
                               {Update, "Update"},
                               {Merge, "Merge"},
                               {PointDelete, "PointDelete"},
                               {RangeDelete, "RangeDelete"},
                               {PointQuery, "PointQuery"},
                               {RangeQuery, "RangeQuery"},
                               })


  class OperationTiming {
  public:
    Operation operation;
    long latency;

    OperationTiming(const Operation operation, const long latency) : operation(operation),
                                                                     latency(latency) {
    }

    NLOHMANN_DEFINE_TYPE_INTRUSIVE(OperationTiming, operation, latency);
  };
}

[[nodiscard]] rocksdb::Status benchmark(
  const std::string &rocksdb_options_filename,
  const std::string &workload_filename,
  const std::string &db_name = "./db"
) {
  std::ifstream workload_file(workload_filename);

  if (!workload_file.is_open()) {
    FAIL("Error: Could not open workload file", rocksdb::Status::PathNotFound());
  }

  std::unique_ptr<rocksdb::DB> db;

  auto [s, opts, read_opts, write_opts] = load_options(rocksdb_options_filename);
  if (!s.ok())
    FAIL("couldn't load options", s);

  s = rocksdb::DB::Open(opts, db_name, &db);
  if (!s.ok())
    FAIL("couldn't open db", s);

#ifdef TIMER
  std::vector<stats::OperationTiming> timings;
#endif
  std::string line;
  while (std::getline(workload_file, line)) {
    const size_t pos = line.find(' ');
    const std::string operation = line.substr(0, pos);
    constexpr size_t space_len = 1;
    const std::string rest = line.substr(pos + space_len);

    if (operation == "I") {
      const size_t pos2 = rest.find(' ');
      const std::string key = rest.substr(0, pos2);
      const std::string value = rest.substr(pos2 + space_len);
#ifdef TIMER
      auto start = hrc::now();
#endif
      s = db->Put(write_opts, key, value);
#ifdef TIMER
      auto latency = std::chrono::duration_cast<ns>(hrc::now() - start);
      timings.emplace_back(stats::Insert, latency.count());
#endif
      if (!s.ok()) fmt::println(stderr, "Error inserting {}", s.ToString());
    } else if (operation == "P") {
      std::string value;
      s = db->Get(read_opts, rest, &value);
      if (!s.ok() && !s.IsNotFound()) fmt::println(stderr, "Error point querying {}", s.ToString());
    } else if (operation == "U") {
      const size_t pos2 = rest.find(' ');
      const std::string key = rest.substr(0, pos2);
      const std::string value = rest.substr(pos2 + space_len);
      s = db->Put(write_opts, rest, value);
      if (!s.ok()) { fmt::println(stderr, "Error updating {}", s.ToString());
}
    } else {
      fmt::println(stderr, "Unknown operation in workload file: {}", operation);
    }
  }

  s = db->Close();
  if (!s.ok())
    FAIL("couldn't close db", s);

  s = rocksdb::DestroyDB(db_name, opts);
  if (!s.ok()) FAIL("couldn't destroy db", s);
#ifdef TIMER
  json timings_json = timings;
  fmt::print("{}", timings_json.dump());
  // timings
#endif

  return rocksdb::Status::OK();
}

int main(const int argc, char *argv[]) {
  if (argc < 3) {
    fmt::println(stderr, "Error: not enough arguments. Usage: {} <rocksdb-options> <workload-file>", argv[0]);
    return EXIT_FAILURE;
  }

  const std::string rocksdb_options_filename = argv[1];
  const std::string workload_filename = argv[2];

  rocksdb::Status s = benchmark(rocksdb_options_filename, workload_filename);
  if (!s.ok())
    FAIL("error running benchmark", s);


  return 0;
}
