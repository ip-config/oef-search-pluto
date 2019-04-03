#pragma once

// Delete bits as needed

#include <string>
#include <utility>
#include <map>
#include <vector>
#include <errno.h>

#include "cpp-sdk/src/cpp/DapInterface.hpp"

class DataStore
{
  //friend std::ostream& operator<<(std::ostream& os, const DataStore &output);
  //friend void swap(DataStore &a, DataStore &b);
private:
  DataStore(const DataStore &other) = delete;
  DataStore &operator=(const DataStore &other) = delete;
  bool operator==(const DataStore &other) = delete;
  bool operator<(const DataStore &other) = delete;

protected:

  class FieldInfo
  {
  public:
    std::string type;
    std::string fieldname;
    std::string tablename;
  };
public:
  using Description = std::map<std::string, std::map<std::string, std::string>>;

  using Key = std::pair<std::string, std::string>;
protected:
  using FieldInfoPtr = std::shared_ptr<FieldInfo>;

  std::vector<FieldInfoPtr> allFields;

  std::map<std::string, FieldInfoPtr> fieldsByShortName;
  std::map<std::pair<std::string, std::string>, FieldInfoPtr> fieldsByFullName;

  const FieldInfoPtr &getFieldByName(const std::string &name) const;
  const FieldInfoPtr &getFieldByNames(const std::string &tablename, const std::string &fieldname) const;

  using Row = std::map<std::string, ValueMessage>;
  using Table = std::map<Key, Row>;
  using Tables = std::map<std::string, Table>;

  Tables tables;

public:
  DataStore()
  {
  }
  virtual ~DataStore()
  {
  }

  void getDescription(Description &d) const
  {
    for(auto fp : allFields)
    {
      d[fp -> tablename][fp -> fieldname] = fp -> type;
    }
  }

  void diagnostics();

  void AddTableField(const std::string &tablename, const std::string &fieldname,
                     const std::string &fieldtype)
  {
    FieldInfoPtr fp = std::make_shared<FieldInfo>();
    fp -> tablename = tablename;
    fp -> fieldname = fieldname;
    fp -> type = fieldtype;

    fieldsByFullName[std::make_pair(tablename, fieldname)] = fp;
    if (fieldsByShortName.find(fieldname) == fieldsByShortName.end())
    {
      fieldsByShortName[fieldname] = fp;
    }

    allFields.push_back(fp);
  }

  void performRemove(const std::string &core, const std::string &agent)
  {
    auto key = std::make_pair(core, agent);
    for(auto &table : tables)
    {
      table.second.erase(key);
    }
  }

  void performUpdate(const std::string &tablename, const std::string &fieldname,
                     const std::string &core, const std::string &agent, const ValueMessage &value);

  void queryAllRows(std::vector<Key> &output,
                      const std::string &target_table_name,
                      const std::string &target_field_name,
                      const std::string &op,
                      const ValueMessage &query_field_value) const;

  void queryRows(std::vector<Key> &output,
                      const std::string &target_table_name,
                      const std::string &target_field_name,
                      const std::string &op,
                      const ValueMessage &query_field_value,
                      google::protobuf::RepeatedPtrField<Identifier>::const_iterator iter,
                      const google::protobuf::RepeatedPtrField<Identifier>::const_iterator &end
                      ) const;
};

//namespace std { template<> void swap(DataStore& lhs, DataStore& rhs) { lhs.swap(rhs); } }
//std::ostream& operator<<(std::ostream& os, const DataStore &output) {}
