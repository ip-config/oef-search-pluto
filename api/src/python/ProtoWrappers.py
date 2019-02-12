from api.src.proto import update_pb2
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from utils.src.python.Logging import has_logger
from dap_api.src.python.DapManager import DapManager
from typing import List
import functools


class ProtoWrapper:
    def __init__(self, cls, *args, **kwargs):
        self.cls = cls
        self.args = args
        self.kwargs = kwargs

    def get_instance(self, data):
        return self.cls(data, *self.args, **self.kwargs)


class ConfigBuilder:
    def __init__(self, cls):
        self.config = {}
        self.cls = cls

    def _merge_dict(self, a, b):
        new = {}
        common = a.keys() & b.keys()
        for l in [a, b]:
            for k in l:
                if k not in common:
                    new[k] = l[k]
        for k in common:
            if type(a[k]) == dict:
                new[k] = self._merge_dict(a[k], b[k])
            elif type(a[k]) == list:
                new[k] = [*a[k], *b[k]]
            else:
                new[k] = b[k]
        return new

    def __getattr__(self, item):
        func = self.cls.data_store[item]

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            self.config = self._merge_dict(self.config, func(*args, **kwargs))
            return self
        return wrapper

    def build(self):
        return self.config


class InvalidAttribute(Exception):
    def __init__(self, name, description, value_type, msg):
        message = "InvalidAttribute: name: {}, description: {}, type: {}! {}".format(name, description, value_type, msg)
        super().__init__(message)

        # Now for your custom code...
        self.name = name
        self.value_type = value_type
        self.description = description
        self.msg = msg


AttributeName = update_pb2.Update.Attribute.Name
_attr_name_to_type = {
            AttributeName.Value("LOCATION"): 9,
            AttributeName.Value("COUNTRY"): 2,
            AttributeName.Value("CITY"): 2,
            AttributeName.Value("SERVICE_DESCRIPTION"): 2,
            AttributeName.Value("NETWORK_ADDRESS"): 10,
            AttributeName.Value("CUSTOM"): 0
        }


class ValueTransformer:
    # TODO: address signature check
    @classmethod
    def address_transformer(cls, address: update_pb2.Update.Address):
        new_address = dap_update_pb2.DapUpdate.Address()
        new_address.ip = address.ip
        new_address.port = address.port
        return new_address

    @classmethod
    def identity_transformer(cls, src):
        return src

    mapping = {
        2: (7, "s", "s", identity_transformer),
        3: (7, "i", "i", identity_transformer),
        4: (4, "f", "f", identity_transformer),
        5: (5, "d", "d", identity_transformer),
        6: (6, "dm", "dm", identity_transformer),
        7: (7, "i32", "i32", identity_transformer),
        8: (8, "b", "b", identity_transformer),
        9: (9, "l", "l", identity_transformer),
        10: (10, "a", "a", address_transformer)
    }

    @classmethod
    def transform(cls, src):
        new_type, src_name, dst_name, transformer = cls.mapping[src.type]
        res = dap_update_pb2.DapUpdate.DapValue()
        res.type = new_type
        getattr(res, dst_name).CopyFrom(transformer(getattr(src, src_name)))
        return res


class UpdateData:
    _table_entry = lambda table, field: {"table": table, "field": field}
    data_store = {
        "default": lambda table, field: {"default": UpdateData._table_entry(table, field)},
        "data_model": lambda table, field: {"data_model": UpdateData._table_entry(table,field)},
        "attribute": lambda attrname, table, field: {"attributes": {attrname: UpdateData._table_entry(table, field)}}
    }

    def __init__(self, origin: update_pb2.Update, db_structure: dict):
        self.origin = origin
        self.db_structure = db_structure
        if type(origin) == update_pb2.Update:
            self._validate_attributes(origin.attributes)

    def _validate_attributes(self, attributes: List[update_pb2.Update.Attribute]) -> bool:
        for attr in attributes:
            exp_type = _attr_name_to_type[attr.name]
            if exp_type > 0 and exp_type != attr.value.type:
                raise InvalidAttribute(attr.name, attr.description, attr.value.type, "Expected type mismatch: {}".format(exp_type))

    def _set_value(self, upd: dap_update_pb2.DapUpdate.DapValue, origin: update_pb2.Update):
        upd.type = 6
        upd.dm.name = origin.data_model.name
        upd.dm.description = origin.data_model.description
        upd.dm.attributes.extend(origin.data_model.attributes)

    def updFromDataModel(self, key, data_model):
        upd = dap_update_pb2.DapUpdate.TableFieldValue()
        upd.tablename = self.db_structure["data_model"]["table"]
        upd.fieldname = self.db_structure["data_model"]["field"]
        upd.key = key
        upd.value.type = 6

        upd.value.dm.name = data_model.name
        upd.value.dm.description = data_model.description
        upd.value.dm.attributes.extend(data_model.attributes)
        return upd

    def updFromAttribute(self, key, attribute):
        upd = dap_update_pb2.DapUpdate.TableFieldValue()
        sdb = self.db_structure["attributes"]
        if attribute.name in sdb:
            db_name = attribute.name
        elif attribute.name == update_pb2.Update.Attribute.Name.CUSTOM:
            if attribute.description < 1:
                raise InvalidAttribute(attribute.name, "", attr.value.type,
                                       "CUSTOM attribute must have a name specified in description filed")
            if attribute.description in sdb:
                db_name = attribute.description
            else:
                db_name = "default"
        upd.tablename = sdb[db_name]["table"]
        upd.fieldname = sdb[db_name]["field"]
        upd.key = key
        upd.value.CopyFrom(ValueTransformer.transform(attribute.value))

    def toDapUpdate(self) -> update_pb2.Update:
        updates = []
        try:
            updates = self.origin.list
        except:
            updates = [self.origin]
        upd_list = []
        for origin in updates:
            key = origin.key
            if len(key) < 1:
                raise InvalidAttribute("Key", "OEFCorePublicKey", "bytes", "Required key field not set!")
            if origin.HasField("data_model"):
                upd_list.append(self.updFromDataModel(key, origin.data_model))
            for attr in origin.attributes:
                upd_list.append(self.updFromAttribute(key, attr))
        upd = dap_update_pb2.DapUpdate()
        upd.update.extend(upd_list)
        return upd


class QueryData:

    @has_logger
    def __init__(self, origin: query_pb2.Query.Model, dap_manager: DapManager):
        self.origin = origin
        self.dap_manager = dap_manager
        if not self.origin:
            self.origin = query_pb2.Query()

    # TODO support for constraints
    def toDapQuery(self):
        return self.dap_manager.makeQuery(self.origin)
