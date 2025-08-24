#include "convenience.h"
#include "rocksdb/db.h"
#include "utilities/options_util.h"

#include <cstdlib>
#include <fstream>
#include <memory>
#include <fmt/base.h>
#include <nlohmann/json.hpp>

#include "iostats_context.h"
#include "perf_context.h"
#include "statistics.h"
#include "../cmake-build-debug/_deps/fmt-src/include/fmt/xchar.h"

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

  rocksdb::Options options(db_opts, cf_descs[0].options);
  options.statistics = rocksdb::CreateDBStatistics();

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
  double percentile(const std::vector<uint64_t> &data, double percentile) {
    if (data.empty()) return 0.0;
    if (percentile < 0.0 || percentile > 100.0) throw std::out_of_range("percentile out of range");

    const size_t len = data.size();
    const double pos = (percentile / 100.0) * static_cast<double>(len - 1); // fractional index
    const auto idx = static_cast<size_t>(pos);
    const double frac = pos - static_cast<double>(idx);

    const auto v1 = static_cast<double>(data[idx]);
    if (idx + 1 < len) {
      const auto v2 = static_cast<double>(data[idx + 1]);
      return (v1 * (1.0 - frac)) + (v2 * frac); // linear interpolation
    }
    return v1;
  }

  void dump_latency(std::ofstream &file, const std::vector<uint64_t> &data, const std::string &operation) {
    file << operation << std::endl;
    file << "p0," << percentile(data, 0) << std::endl;
    file << "p25," << percentile(data, 25) << std::endl;
    file << "p50," << percentile(data, 50) << std::endl;
    file << "p75," << percentile(data, 75) << std::endl;
    file << "p95," << percentile(data, 95) << std::endl;
  }
}

[[nodiscard]] rocksdb::Status benchmark(
  const std::string &rocksdb_options_filename,
  const std::string &workload_filename,
#ifdef STATS
  const std::string &stats_filename,
  const std::string &latency_filename,
#endif
  const std::string &db_name = "./db"
) {
  std::ifstream workload_file(workload_filename);

  if (!workload_file.is_open()) {
    FAIL("Error: Could not open workload file", rocksdb::Status::PathNotFound());
  }
#ifdef STATS
  std::ofstream stats_file(stats_filename);
  std::ofstream latency_file(latency_filename);
#endif // STATS

  std::unique_ptr<rocksdb::DB> db;

  auto [s, opts, read_opts, write_opts] = load_options(rocksdb_options_filename);
  if (!s.ok())
    FAIL("couldn't load options", s);

  s = rocksdb::DB::Open(opts, db_name, &db);
  if (!s.ok())
    FAIL("couldn't open db", s);

#ifdef STATS
  std::vector<uint64_t> latency_insert;
  std::vector<uint64_t> latency_update;
  std::vector<uint64_t> latency_point_query;
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
#ifdef STATS
      auto start = hrc::now();
#endif
      s = db->Put(write_opts, key, value);
#ifdef STATS
      auto latency = std::chrono::duration_cast<ns>(hrc::now() - start);
      latency_insert.push_back(latency.count());
#endif
      if (!s.ok()) fmt::println(stderr, "Error inserting {}", s.ToString());
    } else if (operation == "P") {
      std::string value;
#ifdef STATS
      auto start = hrc::now();
#endif
      s = db->Get(read_opts, rest, &value);
#ifdef STATS
      auto latency = std::chrono::duration_cast<ns>(hrc::now() - start);
      latency_point_query.push_back(latency.count());
#endif
      if (!s.ok() && !s.IsNotFound()) fmt::println(stderr, "Error point querying {}", s.ToString());
    } else if (operation == "U") {
      const size_t pos2 = rest.find(' ');
      const std::string key = rest.substr(0, pos2);
      const std::string value = rest.substr(pos2 + space_len);
#ifdef STATS
      auto start = hrc::now();
#endif
      s = db->Put(write_opts, key, value);
#ifdef STATS
      auto latency = std::chrono::duration_cast<ns>(hrc::now() - start);
      latency_update.push_back(latency.count());
#endif
      if (!s.ok()) {
        fmt::println(stderr, "Error updating {}", s.ToString());
      }
    } else {
      fmt::println(stderr, "Unknown operation in workload file: {}", operation);
    }
  }
#ifdef STATS
  stats_file << fmt::format("[rocksdb::get_perf_context]\n{}\n", rocksdb::get_perf_context()->ToString());
  stats_file << fmt::format("[rocksdb::get_iostats_context]\n{}\n", rocksdb::get_iostats_context()->ToString());
  stats_file << fmt::format("[options.statistics]\n{}\n", opts.statistics->ToString());
#endif // STATS

  s = db->Close();
  if (!s.ok())
    FAIL("couldn't close db", s);

  s = rocksdb::DestroyDB(db_name, opts);
  if (!s.ok())
    FAIL("couldn't destroy db", s);
#ifdef STATS
  stats::dump_latency(latency_file, latency_insert, "insert (ns)");
  stats::dump_latency(latency_file, latency_update, "update (ns)");
  stats::dump_latency(latency_file, latency_point_query, "point query (ns)");
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

#ifdef STATS
  const std::string stats_filename = argv[3];
  const std::string latency_filename = argv[4];
#endif // STATS

  rocksdb::Status s = benchmark(
    rocksdb_options_filename,
    workload_filename
#ifdef STATS
    ,
    stats_filename,
    latency_filename
#endif // STATS
  );
  if (!s.ok())
    FAIL("error running benchmark", s);


  return 0;
}
