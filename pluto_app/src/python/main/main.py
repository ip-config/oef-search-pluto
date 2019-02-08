#!/usr/bin/env python3
from utils.src.python.Logging import configure as configure_logging
from pluto_app.src.python.app import PlutoApp
import sys

if __name__ == "__main__":
    configure_logging()

#    http_port_number = int(sys.argv[1])
#    certificate_file = sys.argv[2]
#    socket_port_number = http_port_number + 1
#    if len(sys.argv) == 4:
#        socket_port_number = sys.argv[3]

    app = PlutoApp.PlutoApp()
    app.run() #http_port_number, socket_port_number, certificate_file)
