#include "cpp_dap_in_memory/src/cpp/InMemoryDap.hpp"
#include "cpp_dap_utils/src/cpp/dap_utils.hpp"

InMemoryDap::InMemoryDap()
{
}

DapDescription InMemoryDap::describe()
{
  DapDescription result;

  DataStore::Description desc;
  store.getDescription(desc);
  for(auto const tablename_table: desc)
  {
    auto new_table = result.add_table();
    new_table -> set_name(tablename_table.first);
    for(auto const fieldname_type: tablename_table.second)
    {
      auto new_field = new_table -> add_field();
      new_field -> set_name(fieldname_type.first);
      new_field -> set_type(fieldname_type.second);
    }
  }

  return result;
}

Successfulness InMemoryDap::configure(const DapDescription &desc)
{
  Successfulness result;
  result.set_success(true);

  for(auto const &table : desc.table())
  {
    auto const &tablename = table.name();
    for(auto const &field : table.field())
    {
      auto const &fieldname = field.name();
      auto const &fieldtype = field.type();

      store.AddTableField(tablename, fieldname, fieldtype);
    }
  }

  return result;
}

Successfulness InMemoryDap::update(const DapUpdate&upd) {
  Successfulness result;
  result.set_success(true);

  for(int i = 0 ;i < upd.update_size(); i++)
  {
    auto tfv = upd.update(i);

    std::string tablename = tfv.tablename();
    std::string fieldname = tfv.fieldname();
    std::string core = tfv.key().core();
    std::string agent = tfv.key().agent();
    DapUpdate::DapValue value = tfv.value();

    ValueMessage constraintValue = dap_utils::DapUpdateDapValueToValueMessage(value);

    try
    {
      store.performUpdate(tablename, fieldname, core, agent, constraintValue);
    }
    catch(DapException &ex)
    {
      result.set_success(false);
      result.add_narrative(ex.what());
    }
  }

  return result;
}

Successfulness InMemoryDap::remove(const DapUpdate &upd) {
  Successfulness result;
  result.set_success(true);

  for(int i = 0 ;i < upd.update_size(); i++)
  {
    auto tfv = upd.update(i);

    std::string core = tfv.key().core();
    std::string agent = tfv.key().agent();

    try
    {
      store.performRemove(core, agent);
    }
    catch(DapException &ex)
    {
      result.set_success(false);
      result.add_narrative(ex.what());
    }
  }

  return result;
}

ConstructQueryMementoResponse InMemoryDap::prepareConstraint(const ConstructQueryConstraintObjectRequest &constraint) {
  ConstructQueryMementoResponse result;

  result.set_success(true);

  size_t size = constraint.ByteSizeLong(); 
  void *buffer = malloc(size);
  constraint.SerializeToArray(buffer, size);
  result.set_memento(buffer,  size);
  free(buffer);

  return result;
}

IdentifierSequence InMemoryDap::execute(const DapExecute &execute) {
  IdentifierSequence result;
  result.set_originator(false);

  auto query_memento = execute.query_memento();
  auto memento = query_memento.memento();
  ConstructQueryConstraintObjectRequest constraint;
  constraint.ParseFromString(memento);

  std::vector<DataStore::Key> output;

  if (execute.input_idents().originator())
  {
    store.queryAllRows(output, constraint.target_table_name(), constraint.target_field_name(),
                       constraint.operator_(), constraint.query_field_value());
  }
  else
  {
    google::protobuf::RepeatedPtrField<Identifier>::const_iterator from = execute.input_idents().identifiers().begin();
    google::protobuf::RepeatedPtrField<Identifier>::const_iterator to = execute.input_idents().identifiers().end();

    store.queryRows(output, constraint.target_table_name(), constraint.target_field_name(),
                    constraint.operator_(), constraint.query_field_value(),
                    from, to);
  }

  for(auto const &ident : output)
  {
    auto r = result.add_identifiers();
    if (ident.first.length() > 0)
    {
      r -> set_core(ident.first);
    }
    if (ident.second.length() > 0)
    {
      r -> set_agent(ident.second);
    }
  }

  return result;
}
