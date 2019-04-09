from api.src.python.BackendRouter import BackendRouter
import functools
from dap_api.src.python.network.DapEndpoints import register_dap_interface_endpoints
from api.src.python.network import start_network as start_network_with_router


def dap_network_support(func=None, *, router_name=None):
    """
        Adds network support for a class. If router_name is not set, then it will create a router
        which will route DapInterface to the decorated class thus the decorated class must implement the DapInterface.

        If router_name is set then it will use that as router and the class doesn't have to implement DapInterface.
        Its very important that the router_name attribute should be set before calling start_network!
    """
    if func is None:
        return functools.partial(dap_network_support, router_name=router_name)

    router_attr_name = router_name if router_name is not None else "__dap_interface_router"

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        dap = args[0]
        if router_attr_name == "__dap_interface_router":
            router = BackendRouter()
            register_dap_interface_endpoints(router, dap)
            setattr(dap, router_attr_name, router)

        def start_network(self, ip: str, socket_port: int, http_port: int = -1, ssl_certificate: str = None,
                          html_dir: str = None):
            self._com = start_network_with_router(getattr(self, router_attr_name), ip, socket_port, http_port,
                                                  ssl_certificate, html_dir)

        def wait(self):
            return self._com.wait()

        setattr(dap, "wait", wait)
        setattr(dap, "start_network", start_network)
        return func(*args, **kwargs)
    return wrapper
