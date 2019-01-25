from api.src.proto import query_pb2, response_pb2


async def backend_entry(query: query_pb2.Query) -> response_pb2.Response:
    resp = response_pb2.Response()
    resp.name = "Hello "+query.name+", I'm Server"
    return resp
