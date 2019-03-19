#pragma once

#include "cpp-sdk/src/cpp/Transport.hpp"

#include "api/src/proto/query.pb.h"


class TransportFactory {
public:
  TransportFactory() = default;
  virtual ~TransportFactory() = default;

  void SetReadCallbacks(std::shared_ptr<Transport> tptr){
    tptr->AddReadCallback<Query>("search", [](Query proto, Transport::TransportPtr tptr){
      std::cout << "QUERY: ";
      std::cout << proto.ttl() << " , " << proto.source_key() << std::endl;
    });
  }
};

