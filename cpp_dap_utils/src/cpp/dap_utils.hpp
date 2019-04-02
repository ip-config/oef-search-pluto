#pragma once

#include "cpp-sdk/src/cpp/DapInterface.hpp"

namespace dap_utils
{
  ValueMessage DapUpdateDapValueToValueMessage(DapUpdate::DapValue value);

  using ValueMessageComparator = std::function<bool(const ValueMessage &, const ValueMessage &)>;

  ValueMessageComparator getOperator(
      const std::string &type_a, const std::string &op, const std::string &type_b
  );
}

