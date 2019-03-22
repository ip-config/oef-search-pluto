import abc
from abc import abstractmethod
from typing import Callable
from typing import List

from dap_api.src.python import DapQueryRepn
from dap_api.src.python import DapQueryResult
from dap_api.src.python import SubQueryInterface
from dap_api.src.protos import dap_interface_pb2
from dap_api.src.protos import dap_description_pb2
from dap_api.src.protos import dap_update_pb2


class DapInterface(abc.ABC):
    def __init__():
        pass

    """This function returns the DAP description which lists the
    tables it hosts, the fields within those tables and the result of
    a lookup on any of those tables.

    Returns:
       DapDescription
    """
    @abstractmethod
    def describe(self) -> dap_description_pb2.DapDescription:
        pass

    """This function will be called with any update to this DAP.

    Args:
      update (dap_update_pb2.DapUpdate): The update for this DAP.

    Returns:
      None
    """
    @abstractmethod
    def update(self, update_data: dap_update_pb2.DapUpdate) -> dap_interface_pb2.Successfulness:
        raise Exception("NOT IMPL")

    """This function will be called when the core wants to remove data from search

    Args:
        remove_data (dap_update_pb2.DapUpdate): The data which needs to be removed

    Returns:
      None
    """
    def remove(self, remove_data: dap_update_pb2.DapUpdate) -> dap_interface_pb2.Successfulness:
        raise Exception("NOT IMPL")

    """Remove all the keys in the update[].key fields from the store.

        Args:
          remove_data(dap_update_pb2.DapUpdate): The update containing removal keys

        Returns:
          bool success indicator
        """

    @abstractmethod
    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        raise Exception("NOT IMPL")

    def prepare(self, proto: dap_interface_pb2.ConstructQueryObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        reply = dap_interface_pb2.ConstructQueryMementoResponse()
        reply.success = False
        return reply

    @abstractmethod
    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        pass


    """This function will be called with parts of the query's AST. If
    the interface can construct a unified query for the whole subtree
    it may do so.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      Either a suitable SubQueryInterface object, or None to let the DapManager handle things.
    """
    #def constructQueryObject(self, dapQueryRepnBranch: DapQueryRepn.DapQueryRepn.Branch) -> SubQueryInterface:
    #    return None

    """This function will be called with leaf nodes of the query's
    AST.  The result should be a SubQueryInterface for the constraint object
    object OR None if the constraint cannot be matched.

    Args:
      update (DapUpdate): The update for this DAP.

    Returns:
      Either a suitable QueryExecutionInterface object, or None to let the DapManager handle things.
    """
    #def constructQueryConstraintObject(self, dapQueryRepnLeaf: DapQueryRepn.DapQueryRepn.Leaf) -> SubQueryInterface:
    #    raise Exception("BAD: constructQueryConstraintObject")



class DapBadUpdateRow(Exception):
    def __init__(
            self,
            message,
            table_name="?TABLE",
            core_key="?COREKEY",
            field_name="?FIELD",
            field_type="?FIELDTYPE",
            value_type="?TYPE",
            value=None
        ):
        self.message = message
        self.table_name = table_name
        self.core_key = core_key
        self.field_name = field_name
        self.value_type = value_type
        self.field_type = field_type
        self.value = value
        super(DapBadUpdateRow, self).__init__(
            "{}: table({}), field({})/({}), value({})/({}), core({})".format(
                message,
                self.table_name,
                self.field_name,
                self.field_type,
                self.value,
                self.value_type,
                self.core_key,
            )
        )

def decodeConstraintValue(valueMessage):
    return {
        'bool':          lambda x: x.b,
        'string':        lambda x: x.s,
        'float':         lambda x: x.f,
        'double':        lambda x: x.d,
        'int32':         lambda x: x.i32,
        'int64':         lambda x: x.i64,

        'bool_list':     lambda x: x.b_s,
        'string_list':   lambda x: x.v_s,
        'float_list':    lambda x: x.v_f,
        'double_list':   lambda x: x.v_d,
        'int32_list':    lambda x: x.v_i32,
        'int64_list':    lambda x: x.v_i64,

        'data_model':    lambda x: x.dm,

        'string_pair':  lambda x: (x.v_s[0], x.v_s[1],),
        'string_pair_list':  lambda x: [ ( x.v_d[i], x.v_d[i+1], ) for i in range(0, len(x.v_d), 2) ],

        'string_range':  lambda x: (x.v_s[0], x.v_s[1],),
        'float_range':   lambda x: (x.v_f[0], x.v_f[1],),
        'double_range':  lambda x: (x.v_d[0], x.v_d[1],),
        'int32_range':     lambda x: (x.v_i32[0], x.v_i32[1],),
        'int64_range':     lambda x: (x.v_i64[0], x.v_i64[1],),

        'location':      lambda x: (x.v_d[0], x.v_d[1],),
        'location_range':lambda x: ((x.v_d[0], x.v_d[1],), (x.v_d[2], x.v_d[3],), ),
        'location_list': lambda x: [ ( x.v_d[i], x.v_d[i+1], ) for i in range(0, len(x.v_d), 2) ],

    }[valueMessage.typecode](valueMessage)

def coresToIdentifierSequence(cores: List[DapQueryResult.DapQueryResult]) -> dap_interface_pb2.IdentifierSequence:
    m = dap_interface_pb2.IdentifierSequence()
    if cores != None:
        m.originator = False
        for c in cores:
            ident = m.identifiers.add()
            ident.CopyFrom(c.asIdentifierProto())
    else:
        m.originator = True
    return m

def encodeConstraintValue(data, typecode):
    valueMessage = dap_interface_pb2.ValueMessage()
    valueMessage.typecode = typecode

    if typecode == 'string':
        valueMessage.s = data
    elif typecode == 'float':
        valueMessage.f = data
    elif typecode == 'double':
        valueMessage.d = data
    elif typecode == 'int32':
        valueMessage.i32 = data
    elif typecode == 'int' or typecode == 'int64':
        valueMessage.typecode = 'int64'
        valueMessage.i64 = data

    elif typecode == 'location':
        valueMessage.v_d.append(data[0])
        valueMessage.v_d.append(data[1])

    elif typecode == 'data_model':
        print("DATA MODEL")
        print(data)

    elif typecode == 'string_list':
        valueMessage.v_s.extend(data)
    elif typecode == 'float_list':
        valueMessage.v_f.extend(data)
    elif typecode == 'double_list':
        valueMessage.v_d.extend(data)
    elif typecode == 'i32_list':
        valueMessage.v_i32.extend(data)
    elif typecode == 'i64_list':
        valueMessage.v_i64.extend(data)

    elif typecode == 'location_list':
        for d in data:
            valueMessage.d.append(d[0])
            valueMessage.d.append(d[1])

    elif typecode == 'string_pair':
        valueMessage.d.append(data[0])
        valueMessage.d.append(data[1])

    elif typecode == 'string_pair_list':
        for d in data:
            valueMessage.d.append(d[0])
            valueMessage.d.append(d[1])

    elif typecode == 'string_range':
        valueMessage.v_s.append(data[0])
        valueMessage.v_s.append(data[1])
    elif typecode == 'float_range':
        valueMessage.v_f.append(data[0])
        valueMessage.v_f.append(data[1])
    elif typecode == 'double_range':
        valueMessage.v_d.append(data[0])
        valueMessage.v_d.append(data[1])
    elif typecode == 'i32_range':
        valueMessage.v_i32.append(data[0])
        valueMessage.v_i32.append(data[1])
    elif typecode == 'i64_range':
        valueMessage.v_i64.append(data[0])
        valueMessage.v_i64.append(data[1])

    elif typecode == 'location_range':
        valueMessage.d.append(data[0][0])
        valueMessage.d.append(data[0][1])
        valueMessage.d.append(data[1][0])
        valueMessage.d.append(data[1][1])

    return valueMessage
