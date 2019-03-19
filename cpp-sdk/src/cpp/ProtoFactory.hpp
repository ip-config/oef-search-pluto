#pragma once

#include <string>
//#include "dap_api/src/protos/dap_subquer"
#include "api/src/proto/query.pb.h"


class ProtoFactory {
public:

  ProtoFactory() = default;
  virtual ~ProtoFactory() = default;

  template <class T> std::shared_ptr<T> create(const std::string& path) {
    if (path == "subquery"){
      return std::make_shared<Query>();
    }
    return nullptr;
  }
};