import traceback
from dap_api.src.python import DapInterface
from dap_api.src.protos import dap_description_pb2
from dap_api.src.python import SubQueryInterface
from dap_api.src.python import ProtoHelpers
from dap_api.src.python.DapInterface import DapBadUpdateRow
from dap_api.src.python import DapQueryRepn
from dap_api.src.protos import dap_update_pb2
from utils.src.python.Logging import has_logger
from dap_api.experimental.python import InMemoryDap


class AddressRegistry(InMemoryDap.InMemoryDap):
    @has_logger
    def __init__(self, name, configuration):
        super().__init__(name, configuration)

    def resolve(self, key):
        address = []
        try:
            for tblname in self.store:
                ckey = (key, b'')
                if ckey in self.store[tblname]:
                    for field in self.structure[tblname]:
                        address.append(self.store[tblname][ckey][field])
        except Exception as e:
            self.warning("No address entry for key: "+key.decode("utf-8")+", details: "+str(e))
            print(self.store)
        return address

    def remove(self, remove_data: dap_update_pb2.DapUpdate.TableFieldValue):
        success = False
        for commit in [ False, True ]:
            upd = remove_data
            if upd:

                k, v = ProtoHelpers.decodeAttributeValueToTypeValue(upd.value)

                if upd.fieldname not in self.fields:
                    raise DapBadUpdateRow("No such field", None, upd.key.core, upd.fieldname, k)
                else:
                    tbname = self.fields[upd.fieldname]["tablename"]
                    ftype = self.fields[upd.fieldname]["type"]

                if ftype != k:
                    raise DapBadUpdateRow("Bad type", tbname, upd.key.core, upd.fieldname, k)

                if commit:
                    success |= self.store[tbname][upd.key.core].pop(upd.fieldname, None) is not None
        return success

    def removeAll(self, key):
        return self.store[self.tablenames[0]].pop(key, None) is not None

