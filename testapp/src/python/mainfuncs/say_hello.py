from testapp.src.protos import a_pb2

def say_hello():
    msg = a_pb2.A()
    msg.data = "Hello world2"
    return msg.SerializeToString()
