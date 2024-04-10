

from typing import Dict
import asyncio

from naja_atra import SessionFactory, AppConf
from naja_atra import get_app_conf, set_session_factory
from naja_atra.models.model_bindings import ModelBindingConf
from naja_atra.http_servers.routing_server import RoutingServer
from naja_atra.request_handlers.http_session_local_impl import LocalSessionFactory
from .wsgi_request_handler import WSGIRequestHandler


version = "1.0.0"


class WSGIProxy(RoutingServer):

    def __init__(self, res_conf, model_binding_conf: ModelBindingConf = ModelBindingConf()):
        super().__init__(res_conf=res_conf, model_binding_conf=model_binding_conf)

    def app_proxy(self, environment, start_response):
        return asyncio.run(self.async_app_proxy(environment, start_response))

    async def async_app_proxy(self, environment, start_response):
        request_handler = WSGIRequestHandler(self, environment, start_response)
        return await request_handler.handle_request()


def __fill_proxy(proxy: RoutingServer, session_factory: SessionFactory, app_conf: AppConf):
    appconf = app_conf or get_app_conf()
    set_session_factory(
        session_factory or appconf.session_factory or LocalSessionFactory())
    filters = appconf._get_filters()
    # filter configuration
    for ft in filters:
        proxy.map_filter(ft)

    request_mappings = appconf._get_request_mappings()
    # request mapping
    for ctr in request_mappings:
        proxy.map_controller(ctr)

    ws_handlers = appconf._get_websocket_handlers()

    for hander in ws_handlers:
        proxy.map_websocket_handler(hander)

    err_pages = appconf._get_error_pages()
    for code, func in err_pages.items():
        proxy.map_error_page(code, func)


def new_wsgi_proxy(resources: Dict[str, str] = {}, session_factory: SessionFactory = None, app_conf: AppConf = None) -> WSGIProxy:
    appconf = app_conf or get_app_conf()
    proxy = WSGIProxy(res_conf=resources,
                      model_binding_conf=appconf.model_binding_conf)
    __fill_proxy(proxy, session_factory, appconf)
    return proxy


_proxy: WSGIProxy = None


def config(resources: Dict[str, str] = {}, session_factory: SessionFactory = None, app_conf: AppConf = None):
    global _proxy
    _proxy = new_wsgi_proxy(resources, session_factory, app_conf)


def app(environment, start_response):
    if _proxy is None:
        config()
    _proxy.app_proxy(environment, start_response)
