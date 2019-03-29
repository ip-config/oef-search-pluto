
from dap_in_memory.src.python import InMemoryDap
from google.protobuf import json_format



def main():
    dap1 = InMemoryDap.InMemoryDap("dap1", {
        'protohash-to-id': {
            'protohash': 'string',
        }
    })
    dap2 = InMemoryDap.InMemoryDap("dap2", {
        'city-to-id': {
            'city': 'string',
        }
    })

    print(json_format.MessageToJson(dap1.describe()))
    print(json_format.MessageToJson(dap2.describe()))

if __name__ == "__main__":
    main()

