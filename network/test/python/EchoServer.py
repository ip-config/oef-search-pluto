from network.src.python.async_socket.AsyncSocket import run_server, communication_handler, Writer
import api.proto.py_pb_query

@communication_handler
def handler(data: bytes, writer: Writer):
    print("got message: ", data)
    writer.write(data)


run_server("localhost", 7500)
