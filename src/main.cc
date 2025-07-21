#include "convenience.h"
#include "rocksdb/db.h"
#include "utilities/options_util.h"
#include <cstdlib>
#include <memory>

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

int failure(const std::string &message, const rocksdb::Status &s) {
  std::cerr << message << ": " << s.ToString() << std::endl;
  return EXIT_FAILURE;
}


int main() {
  std::unique_ptr<rocksdb::DB> db;
  const std::string db_name = "./db";

  auto [s, opts, read_opts, write_opts] = load_options("./rocksdb-vector.ini");
  if (!s.ok()) return failure("couldn't load options", s);

  std::cout << opts.memtable_factory->Name() << std::endl;

  s = rocksdb::DB::Open(opts, db_name, &db);
  // if (!s.ok()) return failure("couldn't open db", s);

  s = db->Put(write_opts, "key 1", "value 1");
  if (!s.ok()) return failure("couldn't put 'key 1'", s);

  std::string value;
  s = db->Get(read_opts, "key 1", &value);
  if (!s.ok()) return failure("couldn't get 'key 1'", s);

  s = db->Close();
  if (!s.ok()) return failure("couldn't close db", s);

  // s = rocksdb::DestroyDB(db_name, opts);
  // if (!s.ok()) return failure("couldn't destroy db", s);

  return EXIT_SUCCESS;
}
