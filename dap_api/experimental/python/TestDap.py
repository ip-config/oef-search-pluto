from dap_api.src.python.network.DapNetworkProxy import DapNetworkProxy
import sys
import inspect
from dap_api.experimental.python.NetworkDapContract import config_contract
from utils.src.python.Logging import configure as configure_logging
from dap_api.src.protos import dap_update_pb2
from fetch_teams.oef_core_protocol import query_pb2
from typing import List


selected_ports = [15000]


def get_attr_b(name, desc, t=2):
    attr1 = query_pb2.Query.Attribute()
    attr1.name = name
    attr1.type = t
    attr1.required = True
    attr1.description = desc
    return attr1


def create_dm(name: str, description: str, attributes: list) -> query_pb2.Query.DataModel:
    dm = query_pb2.Query.DataModel()
    dm.name = name
    dm.description = description
    dm.attributes.extend(attributes)
    return dm


def create_dm_updates(upd):
    dm = create_dm("weatherdata",
                   "All possible weather data.", [
                       get_attr_b("windspeed", "Provides wind speed measurements.", 0),
                       get_attr_b("temperature", "Provides wind speed measurements.", 0),
                       get_attr_b("airpressure", "Provides wind speed measurements.", 0)
                   ])
    upd.tablename = "tablename"
    upd.fieldname = "fieldname"
    upd.value.type = 6
    upd.value.dm.CopyFrom(dm)
    upd.key.core = "LondonCore".encode("utf-8")
    upd.key.agent = "Agent001".encode("utf-8")


def add_value(upd, name, val):
    v1 = upd.value.kv.add()
    v1.key = name
    if type(val) == int:
        v1.value.i = val
    elif type(val) == float:
        v1.value.d = val
    elif type(val) == str:
        v1.value.s = val
    elif type(val) == bool:
        v1.value.b = val
    elif type(val) == dict:
        v1.value.l.lon = val["lon"]
        v1.value.l.lat = val["lat"]


def create_kv_updates(upd):
    upd.tablename = "tablename"
    upd.fieldname = "fieldname"
    upd.value.type = 11
    upd.key.core = "LondonCore".encode("utf-8")
    upd.key.agent = "Agent001".encode("utf-8")
    add_value(upd, "windspeed", 100.)
    add_value(upd, "temperature", 100.)
    #add_value(upd, "airpressure", 1.)


def create_dap_updates() -> List[dap_update_pb2.DapUpdate]:
    #update = dap_update_pb2.DapUpdate()
    #create_dm_updates(update.update.add())
    #create_kv_updates(update.update.add())
    upd1 = dap_update_pb2.DapUpdate.TableFieldValue()
    create_dm_updates(upd1)
    upd2 = dap_update_pb2.DapUpdate.TableFieldValue()
    create_kv_updates(upd2)
    return [upd1, upd2]


def lookup(clss, name):
    for cls in clss:
        if cls[0] == name:
            return cls[1]
    return None


configure_logging()
classes = inspect.getmembers(sys.modules[__name__])
daps = []
updates = create_dap_updates()
for name, conf in config_contract.items():
    cls = lookup(classes, conf["class"])
    if cls is not None and conf["config"]["port"] in selected_ports:
        daps.append(cls(name, conf["config"]))
        dap = daps[-1]
        print("------------------\nDESCRIBE")
        print(dap.describe())
        print("------------------\nUPDATE")
        for upd in updates:
            print(upd)
            ss = upd.SerializeToString()
            print(ss)
            print(dap.update(upd))
        print("------------------\nREMOVE AKA QUERY")
        print(dap.remove(updates[0]))
