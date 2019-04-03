import argparse
import multiprocessing
import time


def run_node(id: int, q: multiprocessing.Queue):
    from network_oef.src.python.FullLocalSearchNode import FullSearchNone
    from utils.src.python.Logging import configure as configure_logging
    configure_logging(id_flag=str(id))

    node = FullSearchNone("search{}".format(id), "127.0.0.1", 10000+id, [{
        "run_py_dap": True,
        "file": "ai_search_engine/src/resources/dap_config.json",
        "port": 20000+id
    }
    ], 7500+id, args.ssl_certificate, "api/src/resources/website")
    print("Node started")
    time.sleep(1)
    con = q.get()
    print("SearchProcess {} got: ".format(id), con)
    node.add_remote_peer(*con)
    node.block()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Test application for PLUTO.')
    parser.add_argument("--ssl_certificate", required=True, type=str, help="specify an SSL certificate PEM file.")
    args = parser.parse_args()

    processes = []
    queues = {}
    for i in range(2):
        q = multiprocessing.Queue()
        p = multiprocessing.Process(target=run_node, args=(i, q))
        p.start()
        processes.append(p)
        queues[i] = q

    time.sleep(2)

    queues[0].put(("127.0.0.1", 10001, "search2"))
    for p in processes:
        p.join()
