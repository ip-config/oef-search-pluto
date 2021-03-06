#define DATASTORE_CPP
#include "DataStore.hpp"

#include <iostream>

#include "cpp_dap_utils/src/cpp/dap_utils.hpp"

const DataStore::FieldInfoPtr &DataStore::getFieldByName(const std::string &name) const
{
  std::stringstream ss(name);
  std::vector<std::string> parts;

  while( ss.good() )
  {
    std::string substr;
    std::getline( ss, substr, '.' );
    parts.push_back( substr );
  }

  if (parts.size() > 2)
  {
    throw DapException(EINVAL, std::string("'") + name + "' is not a valid fieldname (Too many components)");
  }
  if (parts.size() < 1)
  {
    throw DapException(EINVAL, std::string("'") + name + "' is not a valid fieldname (Too short?)");
  }
  for(auto const &part : parts)
  {
    if (part.length() == 0)
    {
      throw DapException(EINVAL, std::string("'") + name + "' is not a valid fieldname (Missing component? Leading dot?)");
    }
  }

  if (parts.size() == 1)
  {
    auto iter = fieldsByShortName.find(parts[0]);
    if (iter != fieldsByShortName.end())
    {
      return iter -> second;
    }
  }
  else
  {
    auto iter = fieldsByFullName.find(std::make_pair(parts[0], parts[1]));
    if (iter != fieldsByFullName.end())
    {
      return iter -> second;
    }
  }

  throw DapException(ENOENT, std::string("'") + name + "' is not a valid fieldname (Not stored in structure)");
}

const DataStore::FieldInfoPtr &DataStore::getFieldByNames(const std::string &tablename, const std::string &fieldname) const
{
  auto iter = fieldsByFullName.find(std::make_pair(tablename, fieldname));
  if (iter != fieldsByFullName.end())
  {
    return iter -> second;
  }
  throw DapException(ENOENT, std::string("'") + tablename + "." + fieldname + "' is not a valid fieldname (Not stored in structure)");
}

void DataStore::performUpdate(const std::string &tablename, const std::string &fieldname,
                              const std::string &core, const std::string &agent, const ValueMessage &value)
{
//  diagnostics();
//  std::cout << " tablename= " << tablename<< std::endl;
//  std::cout << " fieldname= " << fieldname<< std::endl;
//  std::cout << " core= " << core<< std::endl;
//  std::cout << " agent= " << agent<< std::endl;

  auto fp = getFieldByNames(tablename, fieldname);
  if (fp -> type != value.typecode())
  {
    throw DapException(EINVAL, std::string("'") + tablename + "." + fieldname + "' is "  + fp -> type + " and cannot be assigned " + value.typecode());
  }

  auto key = std::make_pair(core, agent);

  Table &table = tables[fp -> tablename];
  Row &row = table[key];
  row[fp -> fieldname] = value;

}

void DataStore::diagnostics()
{
  std::cout << "tables size:" << tables.size() << std::endl;
  for(auto const &table : tables)
  {
    std::cout << "table " << table.first << " size:" << table.second.size() << std::endl;
  }
}

void DataStore::queryAllRows(std::vector<DataStore::Key> &output,
                             const std::string &target_table_name,
                             const std::string &target_field_name,
                             const std::string &op,
                             const ValueMessage &query_field_value) const
{
  auto fp = getFieldByNames(target_table_name, target_field_name);
  auto opfunc = dap_utils::getOperator(fp->type, op, query_field_value.typecode());

  auto table = tables.find(target_table_name) -> second;

//  std::cout << " target_table_name= " << target_table_name<< std::endl;
//  std::cout << " target_field_name= " << target_field_name<< std::endl;
//  std::cout << " op= " << op<< std::endl;
//  std::cout << " table:" << table.size() << std::endl;

  for(auto const &key_and_row : table)
  {
    auto const &row = key_and_row.second;

    //std::cout << "Examine:"<<key_and_row.first.second << std::endl;

    auto fv_iter = row.find(fp -> fieldname);
    if (fv_iter == row.end())
    {
      continue;
    }

    auto const &fv = fv_iter -> second;
    if (opfunc(fv, query_field_value))
    {
      output.push_back(key_and_row.first);
    }
  }
}

void DataStore::queryRows(std::vector<DataStore::Key> &output,
               const std::string &target_table_name,
               const std::string &target_field_name,
               const std::string &op,
               const ValueMessage &query_field_value,
               google::protobuf::RepeatedPtrField<Identifier>::const_iterator iter,
               const google::protobuf::RepeatedPtrField<Identifier>::const_iterator &end
               ) const
{
  auto fp = getFieldByNames(target_table_name, target_field_name);
  auto opfunc = dap_utils::getOperator(fp->type, op, query_field_value.typecode());
  auto table = tables.find(target_table_name) -> second;

  while(iter != end)
  {
    auto row_iter = table.find(std::make_pair( iter->core(), iter->agent() ));
    if (row_iter != table.end())
    {
      auto const &row = row_iter -> second;
      auto fv_iter = row.find(fp -> fieldname);
      if (fv_iter != row.end())
      {
        auto const &fv = fv_iter -> second;
        if (opfunc(fv, query_field_value))
        {
          output.push_back(row_iter -> first);
        }
      }
    }

    ++iter;
  }
}
