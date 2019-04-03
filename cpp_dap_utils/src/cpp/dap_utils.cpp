#define DAP_UTILS_CPP
#include "cpp_dap_utils/src/cpp/dap_utils.hpp"

static const char* typeCodeToTypestring[] =
  {
    "TYPE_0_NOT_DEFINED", // 0
    "TYPE_1_NOT_DEFINED", // 1
    "string",             // 2
    "int64",              // 3
    "float",              // 4
    "double",             // 5
    "data_model",         // 6
    "int32",              // 7
    "bool",               // 8
    "location",           // 9
    "address",            // 10
    "keyvalues",          // 11
  };

namespace dap_utils
{
  template<typename PROTOBUF_RPT_FIELD, class VALUE>
  bool search(const VALUE &val, const PROTOBUF_RPT_FIELD &fld)
  {
    auto iter = fld.begin();
    while(iter != fld.end())
    {
      if (*iter == val)
      {
        return true;
      }
    }
    return false;
  }
}

static std::map<
  std::tuple<std::string, std::string, std::string>,
  dap_utils::ValueMessageComparator
  > valueMessageComparators = {
  { { "string", "==", "string" }, [](const ValueMessage &a, const ValueMessage &b){ return a.s() == b.s(); } },
  { { "string", "!=", "string" }, [](const ValueMessage &a, const ValueMessage &b){ return a.s() == b.s(); } },
  { { "string", ">", "string" },  [](const ValueMessage &a, const ValueMessage &b){ return a.s() == b.s(); } },
  { { "string", "<", "string" },  [](const ValueMessage &a, const ValueMessage &b){ return a.s() == b.s(); } },
  { { "string", ">=", "string" }, [](const ValueMessage &a, const ValueMessage &b){ return a.s() == b.s(); } },
  { { "string", "<=", "string" }, [](const ValueMessage &a, const ValueMessage &b){ return a.s() == b.s(); } },
  
  { { "bool", "==", "bool" }, [](const ValueMessage &a, const ValueMessage &b){ return a.b() == b.b(); } },
  { { "bool", "!=", "bool" }, [](const ValueMessage &a, const ValueMessage &b){ return a.b() == b.b(); } },

  { { "int64", "==", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() == b.i64(); } },
  { { "int64", "!=", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() != b.i64(); } },
  { { "int64", ">", "int64" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i64() >  b.i64(); } },
  { { "int64", "<", "int64" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i64() <  b.i64(); } },
  { { "int64", ">=", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() >= b.i64(); } },
  { { "int64", "<=", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() <= b.i64(); } },

  { { "int32", "==", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() == b.i64(); } },
  { { "int32", "!=", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() != b.i64(); } },
  { { "int32", ">", "int64" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i32() >  b.i64(); } },
  { { "int32", "<", "int64" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i32() <  b.i64(); } },
  { { "int32", ">=", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() >= b.i64(); } },
  { { "int32", "<=", "int64" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() <= b.i64(); } },

  { { "int64", "==", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() == b.i32(); } },
  { { "int64", "!=", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() != b.i32(); } },
  { { "int64", ">", "int32" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i64() >  b.i32(); } },
  { { "int64", "<", "int32" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i64() <  b.i32(); } },
  { { "int64", ">=", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() >= b.i32(); } },
  { { "int64", "<=", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i64() <= b.i32(); } },

  { { "int32", "==", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() == b.i32(); } },
  { { "int32", "!=", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() != b.i32(); } },
  { { "int32", ">", "int32" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i32() >  b.i32(); } },
  { { "int32", "<", "int32" },  [](const ValueMessage &a, const ValueMessage &b){ return a.i32() <  b.i32(); } },
  { { "int32", ">=", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() >= b.i32(); } },
  { { "int32", "<=", "int32" }, [](const ValueMessage &a, const ValueMessage &b){ return a.i32() <= b.i32(); } },

  { { "double", "==", "double" }, [](const ValueMessage &a, const ValueMessage &b){ return a.d() == b.d(); } },
  { { "double", "!=", "double" }, [](const ValueMessage &a, const ValueMessage &b){ return a.d() != b.d(); } },
  { { "double", ">", "double" },  [](const ValueMessage &a, const ValueMessage &b){ return a.d() >  b.d(); } },
  { { "double", "<", "double" },  [](const ValueMessage &a, const ValueMessage &b){ return a.d() <  b.d(); } },
  { { "double", ">=", "double" }, [](const ValueMessage &a, const ValueMessage &b){ return a.d() >= b.d(); } },
  { { "double", "<=", "double" }, [](const ValueMessage &a, const ValueMessage &b){ return a.d() <= b.d(); } },

  { { "float", "==", "double" },  [](const ValueMessage &a, const ValueMessage &b){ return a.f() == b.d(); } },
  { { "float", "!=", "double" },  [](const ValueMessage &a, const ValueMessage &b){ return a.f() != b.d(); } },
  { { "float", ">", "double" },   [](const ValueMessage &a, const ValueMessage &b){ return a.f() >  b.d(); } },
  { { "float", "<", "double" },   [](const ValueMessage &a, const ValueMessage &b){ return a.f() <  b.d(); } },
  { { "float", ">=", "double" },  [](const ValueMessage &a, const ValueMessage &b){ return a.f() >= b.d(); } },
  { { "float", "<=", "double" },  [](const ValueMessage &a, const ValueMessage &b){ return a.f() <= b.d(); } },

  { { "double", "==", "float" },  [](const ValueMessage &a, const ValueMessage &b){ return a.d() == b.f(); } },
  { { "double", "!=", "float" },  [](const ValueMessage &a, const ValueMessage &b){ return a.d() != b.f(); } },
  { { "double", ">", "float" },   [](const ValueMessage &a, const ValueMessage &b){ return a.d() >  b.f(); } },
  { { "double", "<", "float" },   [](const ValueMessage &a, const ValueMessage &b){ return a.d() <  b.f(); } },
  { { "double", ">=", "float" },  [](const ValueMessage &a, const ValueMessage &b){ return a.d() >= b.f(); } },
  { { "double", "<=", "float" },  [](const ValueMessage &a, const ValueMessage &b){ return a.d() <= b.f(); } },

  { { "float", "==", "float" },   [](const ValueMessage &a, const ValueMessage &b){ return a.f() == b.f(); } },
  { { "float", "!=", "float" },   [](const ValueMessage &a, const ValueMessage &b){ return a.f() != b.f(); } },
  { { "float", ">", "float" },    [](const ValueMessage &a, const ValueMessage &b){ return a.f() >  b.f(); } },
  { { "float", "<", "float" },    [](const ValueMessage &a, const ValueMessage &b){ return a.f() <  b.f(); } },
  { { "float", ">=", "float" },   [](const ValueMessage &a, const ValueMessage &b){ return a.f() >= b.f(); } },
  { { "float", "<=", "float" },   [](const ValueMessage &a, const ValueMessage &b){ return a.f() <= b.f(); } },

  { { "float",  "IN",    "float_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.f(), b.v_f()); } },
  { { "float",  "NOTIN", "float_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.f(), b.v_f()); } },
  { { "float",  "IN",    "double_list" }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.f(), b.v_d()); } },
  { { "float",  "NOTIN", "double_list" }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.f(), b.v_d()); } },
  { { "double", "IN",    "double_list" }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.d(), b.v_d()); } },
  { { "double", "NOTIN", "double_list" }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.d(), b.v_d()); } },
  { { "double", "IN",    "float_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.d(), b.v_f()); } },
  { { "double", "NOTIN", "float_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.d(), b.v_f()); } },

  { { "int32",  "IN",    "int32_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.i32(), b.v_i32()); } },
  { { "int32",  "NOTIN", "int32_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.i32(), b.v_i32()); } },
  { { "int32",  "IN",    "int64_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.i32(), b.v_i64()); } },
  { { "int32",  "NOTIN", "int64_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.i32(), b.v_i64()); } },
  { { "int64",  "IN",    "int64_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.i64(), b.v_i64()); } },
  { { "int64",  "NOTIN", "int64_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.i64(), b.v_i64()); } },
  { { "int64",  "IN",    "int32_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.i64(), b.v_i32()); } },
  { { "int64",  "NOTIN", "int32_list"  }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.i64(), b.v_i32()); } },

  { { "string", "IN",    "string_list" }, [](const ValueMessage &a, const ValueMessage &b){ return  dap_utils::search(a.s(), b.v_s()); } },
  { { "string", "NOTIN", "string_list" }, [](const ValueMessage &a, const ValueMessage &b){ return !dap_utils::search(a.s(), b.v_s()); } },
};

namespace dap_utils
{
  ValueMessage DapUpdateDapValueToValueMessage(DapUpdate::DapValue value)
  {
    ValueMessage vm;

    switch(value.type())
    {
    case 2:
      vm.set_typecode(typeCodeToTypestring[value.type()]);
      vm.set_s(value.s());
      break;

    case 3:
      vm.set_typecode(typeCodeToTypestring[value.type()]);
      vm.set_i32(value.i());
      break;

    case 4:
      vm.set_typecode(typeCodeToTypestring[value.type()]);
      vm.set_f(value.f());
      break;

    case 5:
      vm.set_typecode(typeCodeToTypestring[value.type()]);
      vm.set_d(value.d());
      break;

    case 7:
      vm.set_typecode(typeCodeToTypestring[value.type()]);
      vm.set_i32(value.i32());
      break;

    case 8:
      vm.set_typecode(typeCodeToTypestring[value.type()]);
      vm.set_b(value.b());
      break;

    case 9:
      vm.set_typecode(typeCodeToTypestring[value.type()]);
      vm.set_v_d(0, value.l().lat());
      vm.set_v_d(1, value.l().lon());
      break;

    case 0:
    case 1:
    case 6:
    case 10:
    case 11:
      throw DapException(EINVAL, std::string("type not supported in ValueMessage:") + typeCodeToTypestring[value.type()]);

    default:
      throw DapException(EINVAL, std::string("type not supported in ValueMessage: ") + std::to_string(value.type()));

    }
    return vm;
  }

  std::function<bool(const ValueMessage &a, const ValueMessage &b)> getOperator(
      const std::string &type_a, const std::string &op, const std::string &type_b
  )
  {
    auto k = std::make_tuple(type_a, op, type_b);
    auto iter = valueMessageComparators.find(k);
    if (iter != valueMessageComparators.end())
    {
      return iter -> second;
    }
    return nullptr;
  }

}
