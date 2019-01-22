from src.protos.testapp import a_pb2

def say_hello():
    msg = a_pb2.A()
    msg.data = "Hello world"
    return msg.SerializeToString()
