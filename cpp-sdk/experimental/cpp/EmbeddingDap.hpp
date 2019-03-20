#pragma once

#include "cpp-sdk/src/cpp/DapInterface.hpp"


class EmbeddingDap : public DapInterface {
public:
  EmbeddingDap() = default;
  virtual ~EmbeddingDap() = default;

  virtual DapDescription describe() {
    DapDescription proto;
    proto.set_name("Hello");
    return proto;
  }

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
