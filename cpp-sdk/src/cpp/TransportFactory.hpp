#pragma once

#include "Transport.hpp"


class TransportFactory {
public:
  TransportFactory() = default;
  virtual ~TransportFactory() = default;

  virtual void SetReadCallbacks(std::shared_ptr<Transport> tptr) = 0;
};