#pragma once

#include "cpp-sdk/src/cpp/DapInterface.hpp"
#include "cpp_dap_in_memory/src/cpp/DataStore.hpp"

class InMemoryDap : public DapInterface {
public:
  InMemoryDap();

  virtual ~InMemoryDap() = default;

  virtual Successfulness configure(const DapDescription&);

  virtual DapDescription describe();

  virtual Successfulness update(const DapUpdate_TableFieldValue&);

  virtual Successfulness remove(const DapUpdate_TableFieldValue&);

  virtual ConstructQueryMementoResponse prepareConstraint(const ConstructQueryConstraintObjectRequest&);

  virtual ConstructQueryMementoResponse prepare(const ConstructQueryObjectRequest&) {
    ConstructQueryMementoResponse proto;
    proto.set_success(false);
    return proto;
  }

  virtual IdentifierSequence execute(const DapExecute&);
protected:
  DataStore store;
};
