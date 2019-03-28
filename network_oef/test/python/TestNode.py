from network_oef.src.python.FullLocalSearchNode import FullSearchNone
from utils.src.python.Logging import configure as configure_logging
import argparse


if __name__ == "__main__":
    configure_logging()

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--ssl_certificate", required=True, type=str, help="specify an SSL certificate PEM file.")
    args = parser.parse_args()

    node1 = FullSearchNone("search1", 10000, [{
        "file": "ai_search_engine/src/resources/dap_config.json",
        "port": 20000
        }
    ], 7500, args.ssl_certificate, "api/src/resources/website")

