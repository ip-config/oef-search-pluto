from typing import Callable
import json

from dap_api.src.protos import dap_description_pb2
from dap_api.src.protos import dap_update_pb2
from dap_api.src.protos import dap_interface_pb2

from dap_api.src.python import DapInterface
from utils.src.python.Logging import has_logger
from dap_api.src.python import ProtoHelpers
from dap_api.src.python import DapOperatorFactory

class DapAttributeStore(DapInterface.DapInterface):

    # configuration is a JSON deserialised config object.
    # structure is a map of tablename -> { fieldname -> type}

    class StoredFieldValue(object):
        def __init__(self, ft = None, fv = None):
            self.field_value = fv
            self.field_type = ft

        def match(self, operatorFactory, query_settings):
            f = operatorFactory.lookup(self.field_type, query_settings['operator'], query_settings['query_field_type'])
            if not f:
                return False
            return f(query_settings['query_field_value'], self.field_value)
            return True

        def printable(self):
            return "{} ({})".format(
                self.field_value,
                self.field_type,
            )

    @has_logger
    def __init__(self, name, configuration):
        self.name = name
        self.table = {}
        self.operatorFactory = DapOperatorFactory.DapOperatorFactory()

    def describe(self):
        result = dap_description_pb2.DapDescription()
        result.name = self.name

        star_table = result.table.add()
        star_table.name = '*'

        star_field = star_table.field.add()
        star_field.name = '/them\\..*/'
        star_field.type = '*'

        return result

    def print(self):
        for k in self.table.keys():
            self.error("{},{}:".format(k[0],k[1]))
            for kk in self.table[k].keys():
                self.error("    "+kk+":")
                self.error("        " + self.table[k][kk].printable())

    def prepareConstraint(self, proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        query_settings = {}

        target_field_name = proto.target_field_name
        if target_field_name[0:5] != 'them.':
            target_field_name = 'them.' + target_field_name

        query_settings['target_field_name'] = target_field_name
        query_settings['target_field_type'] = proto.target_field_type
        query_settings['operator'] = proto.operator
        query_settings['query_field_type'] = proto.query_field_type
        query_settings['query_field_value'] = DapInterface.decodeConstraintValue(proto.query_field_value)

        r = dap_interface_pb2.ConstructQueryMementoResponse()
        r.memento = json.dumps(query_settings).encode('utf8')
        r.success = True
        return r

    def test(self, row: dict, query_settings: dict) -> bool:
        target_field = row.get(query_settings['target_field_name'], None)
        if target_field:
            return target_field.match(self.operatorFactory, query_settings)

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        input_idents = proto.input_idents
        query_memento = proto.query_memento
        query_settings = json.loads(query_memento.memento.decode("utf-8"))

        result = dap_interface_pb2.IdentifierSequence()
        if input_idents.originator:
            for row_key, row in self.table.items():
                core_ident, agent_ident = row_key
                if self.test(row, query_settings):
                    i = result.identifiers.add()
                    i.core = core_ident
                    i.agent = agent_ident
        else:
            for key in input_idents.identifiers:
                core_ident, agent_ident = key.core, key.agent
                row = table.get((core_ident, agent_ident), None)
                if row != None and self.test(row, query_settings):
                    i = result.identifiers.add()
                    i.core = core_ident
                    i.agent = agent_ident
        return result

    def update(self, tfv: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness()
        r.success = True

        if tfv:
            row_key = (tfv.key.core, tfv.key.agent)
            core_ident, agent_ident = row_key

            field_type, field_value = ProtoHelpers.decodeAttributeValueInfoToPythonType(tfv.value)
            if field_type == "key-type-value_list":
                for k,t,v in field_value:
                    self.table.setdefault(row_key, {})[k] = DapAttributeStore.StoredFieldValue(ft=t, fv=v)
            else:
                target_field_name = tfv.fieldname
                if target_field_name[0:5] != 'them.':
                    target_field_name = 'them.' + target_field_name
                #self.log.info("INSERT: core={}, agent={}".format(core_ident, agent_ident))
                self.table.setdefault(row_key, {})[target_field_name] = DapAttributeStore.StoredFieldValue(ft=field_type, fv=field_value)

        return r

    def remove(self, remove_data: dap_update_pb2.DapUpdate) -> dap_interface_pb2.Successfulness:
        r = dap_interface_pb2.Successfulness()
        r.success = True

        success = False
        for commit in [ False, True ]:
            row_key = (remove_data.key.core, remove_data.key.agent)
            core_ident, agent_ident = row_key
            for tbname in self.store.keys():
                if commit:
                    self.store[tbname].pop(row_key)
            if not r.success:
                break
        return r
