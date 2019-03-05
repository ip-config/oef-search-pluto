import threading

server_ref = None
from fetch_teams.bottle import bottle
from wsgiref.simple_server import make_server
from fetch_teams.bottle.bottle import ServerAdapter
from fetch_teams.bottle.bottle import WSGIRefServer

class MyServer(WSGIRefServer):
    def run(self, app): # pragma: no cover
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self): # Prevent reverse DNS lookups please.
                return self.client_address[0]
            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls  = self.options.get('server_class', WSGIServer)

        if ':' in self.host: # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        srv = make_server(self.host, self.port, app) #, server_cls, handler_cls)
        self.srv = srv ### THIS IS THE ONLY CHANGE TO THE ORIGINAL CLASS METHOD!
        srv.serve_forever()

    def shutdown(self): ### ADD SHUTDOWN METHOD.
        self.srv.shutdown()
        # self.server.server_close()


class ThreadedWebserver(object):
    def __init__(self, http_port, app):
        self.http_port = http_port
        self.app = app

        self.server = MyServer(host="0.0.0.0", port=self.http_port)
        self.thread = ThreadedWebserver.ServingThread(self.server, self.app)

    def run(self):
        print("WEB THREAD START")
        self.thread.start()

    def stop(self):
        print("WEB THREAD STOP")
        self.server.shutdown()
        self.thread.join()

    class ServingThread(threading.Thread):
        def __init__(self, server, app):
            super().__init__()
            self.app = app
            self.server = server

        def run(self):
            print("WEB SERVER START")
            self.server.run(self.app)
            print("WEB SERVER STOP")
