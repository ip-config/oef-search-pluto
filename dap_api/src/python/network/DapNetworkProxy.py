from dap_api.src.python.DapInterface import DapInterface
from dap_api.src.protos.dap_update_pb2 import DapUpdate
from dap_api.src.protos import dap_interface_pb2, dap_update_pb2, dap_description_pb2
from utils.src.python.Logging import has_logger
import json
from network.src.python.socket.SyncSocket import ClientSocket


class DapNetworkProxy(DapInterface):
    @has_logger
    def __init__(self, name, configuration):
        self.host = configuration["host"]
        self.port = configuration["port"]
        self.log.update_local_name(name+"@"+self.host+":"+str(self.port))
        self.info("Opening connection...")
        self.client = ClientSocket(self.host, self.port, self.log)

    def inject_w2v(self, *args, **kwargs):
        pass

    def close(self):
        self.client.close()

    def _call(self, path, data_in, output_type):
        request = data_in.SerializeToString()
        self.warning("REQUEST=" + str(request))

        response = self.client.call(path, request)
        proto = output_type()
        if not response.success:
            self.error("Error response for uri %s, code: %d, reason: %s", response.uri, response.error_code,
                       response.msg())
            return proto
        try:
            proto.ParseFromString(response.data)
        except:
            try:
                sproto = dap_interface_pb2.Successfulness()
                sproto.ParseFromString(response.data)
                if not sproto.success:
                    self.error("Dap failure: code %d, message: %s", sproto.errorcode, sproto.narrative)
                else:
                    self.error("Unknown failure! Message: %s", sproto.message)
            except:
                self.exception("Unknown error!")
        return proto

    def describe(self) -> dap_description_pb2.DapDescription:
        data_in = dap_interface_pb2.NoInputParameter()
        self.warning("DapNetworkProxy::CALLING DESCRIBE:")
        result = self._call("describe", data_in, dap_description_pb2.DapDescription)
        self.warning("DapNetworkProxy::DESCRIBE:", str(result))
        return result


    """This function will be called with any update to this DAP.

    Args:
      update (dap_update_pb2.DapUpdate): The update for this DAP.

    Returns:
      None
    """

    def update(self, update_data: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        return self._call("update", update_data, dap_interface_pb2.Successfulness)


    """This function will be called when the core wants to remove data from search

    Args:
        remove_data (dap_update_pb2.DapUpdate): The data which needs to be removed

    Returns:
      None
    """

    def remove(self, remove_data: dap_update_pb2.DapUpdate.TableFieldValue) -> dap_interface_pb2.Successfulness:
        return self._call("remove", remove_data, dap_interface_pb2.Successfulness)

    """Remove all the keys in the update[].key fields from the store.

        Args:
          remove_data(dap_update_pb2.DapUpdate): The update containing removal keys

        Returns:
          bool success indicator
        """

    def prepareConstraint(self,
                          proto: dap_interface_pb2.ConstructQueryConstraintObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        return self._call("prepareConstraint", proto, dap_interface_pb2.ConstructQueryMementoResponse)

    def prepare(self,
                proto: dap_interface_pb2.ConstructQueryObjectRequest) -> dap_interface_pb2.ConstructQueryMementoResponse:
        return self._call("prepare", proto, dap_interface_pb2.ConstructQueryMementoResponse)

    def execute(self, proto: dap_interface_pb2.DapExecute) -> dap_interface_pb2.IdentifierSequence:
        return self._call("execute", proto, dap_interface_pb2.IdentifierSequence)


def _config_from_dap_json(file, cls = "DapNetworkProxy"):
    f = open(file)
    j = json.load(f)

    config = dict()
    c = config[j["description"]["name"]] = dict()

    if cls is None:
        cls = j["class"]

    c["class"] = cls
    c["config"] = dict()
    c["config"]["host"] = j["host"]
    c["config"]["port"] = j["port"]
    c["config"]["structure"] = dict()

    cs = c["config"]["structure"]

    tb = j["description"]["table"]
    if tb:
        cs[tb["name"]] = dict()
        for f in tb["field"]:
            cs[tb["name"]][f["name"]] = f["type"]
    return config


def proxy_config_from_dap_json(file):
    return _config_from_dap_json(file)


def config_from_dap_json(file):
    return _config_from_dap_json(file, None)
