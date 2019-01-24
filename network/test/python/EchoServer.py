from network.src.python.async_socket.AsyncSocket import run_server, communication_handler, Writer


@communication_handler
def handler(data: bytes, writer: Writer):
    print("got message: ", data)
    writer.write(data)


run_server("localhost", 7500)
