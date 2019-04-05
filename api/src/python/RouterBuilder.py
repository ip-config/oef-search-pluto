from api.src.python.BackendRouter import BackendRouter
from api.src.python.core.SearchEndpoint import SearchEndpoint
from api.src.python.core.UpdateEndpoint import UpdateEndpoint, BlkUpdateEndpoint
from api.src.python.core.RemoveEndpoint import RemoveEndpoint
from api.src.python.director.LocationEndpoint import LocationEndpoint


class CoreAPIRouterBuilder:
    def __init__(self):
        self._router = BackendRouter()
        self._search_endpoint = None
        self._update_endpoint = None
        self._remove_endpoint = None
        self._blk_update_endpoint = None
        self._dap_manager = None
        self._name = ""

    def set_name(self, name):
        self._name = name
        return self

    def add_dap_manager(self, dap_manager):
        self._dap_manager = dap_manager
        return self

    def add_search_wrapper(self, search_wrapper):
        self._search_endpoint = SearchEndpoint(self._dap_manager, search_wrapper)
        return self

    def add_update_wrapper(self, update_wrapper):
        self._update_endpoint = UpdateEndpoint(self._dap_manager, update_wrapper)
        self._blk_update_endpoint = BlkUpdateEndpoint(self._dap_manager, update_wrapper)
        self._remove_endpoint = RemoveEndpoint(self._dap_manager, update_wrapper)
        return self

    def build(self):
        self._router.register_response_merger(self._search_endpoint)
        self._router.register_serializer("search", self._search_endpoint)
        self._router.register_handler("search", self._search_endpoint)
        self._router.register_serializer("update", self._update_endpoint)
        self._router.register_handler("update", self._update_endpoint)
        self._router.register_serializer("blk_update", self._blk_update_endpoint)
        self._router.register_handler("blk_update", self._blk_update_endpoint)
        self._router.register_serializer("remove", self._remove_endpoint)
        self._router.register_handler("remove", self._remove_endpoint)
        if len(self._name) > 0:
            self._router.name = self._name
        return self._router

    def get_not_initialized_router(self):
        return self._router


class DirectorAPIRouterBuilder:
    def __init__(self):
        self._router = BackendRouter()
        self._name = ""
        self._location_endpoint = LocationEndpoint()

    def set_name(self, name):
        self._name = name
        return self

    def build(self):
        self._router.register_serializer("location", self._location_endpoint)
        self._router.register_handler("location", self._location_endpoint)
        return self._router
