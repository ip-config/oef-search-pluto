#!/usr/bin/env python3
from utils.src.python.Logging import configure as configure_logging
from pluto_app.src.python.app import PlutoApp
from api.src.python.CommunicationHandler import socket_server, http_server, CommunicationHandler
import argparse


if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--ssl_certificate", required=True, type=str, help="specify an SSL certificate PEM file.")
    parser.add_argument("--http_port", required=True, type=int, help="which port to run the HTTP interface on.")
    parser.add_argument("--socket_port", required=True, type=int, help="which port to run the socket interface on.")
    parser.add_argument("--html_dir", required=False, type=str, help="where ", default="api/src/resources/website")
    args = parser.parse_args()

    com = CommunicationHandler(2)
    com.add(socket_server, "0.0.0.0", args.socket_port)
    com.add(http_server, "0.0.0.0", args.http_port, args.ssl_certificate, args.html_dir)

    app = PlutoApp.PlutoApp()
    app.run(com)
