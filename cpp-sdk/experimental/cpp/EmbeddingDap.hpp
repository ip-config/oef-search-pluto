#pragma once

#include "cpp-sdk/src/cpp/DapInterface.hpp"


class EmbeddingDap : public DapInterface {
public:
  EmbeddingDap(const DapDescription& description)
   : DapInterface(description)
  {
  }
  virtual ~EmbeddingDap() = default;

  virtual Successfulness update(const DapUpdate&) {
    Successfulness proto;
    return proto;
  }

  virtual Successfulness remove(const DapUpdate&) {
    Successfulness proto;
    return proto;
  }

  virtual ConstructQueryMementoResponse prepareConstraint(const ConstructQueryConstraintObjectRequest&) {
    ConstructQueryMementoResponse proto;
    return proto;
  }

  virtual ConstructQueryMementoResponse prepare(const ConstructQueryObjectRequest&) {
    ConstructQueryMementoResponse proto;
    return proto;
  }

  virtual DapExecute execute(const IdentifierSequence&) {
    DapExecute proto;
    return proto;
  }
};
