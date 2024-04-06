# QuickGrpc-py

This is a simple framework to help your kickstart your grpc service development in python, and to publish the same for someone to invoke...

Let's go

Here's the proto file

```protobuf
syntax = "proto3";

service Greet{
    rpc hi(Inp) returns (Out);
    rpc bye(Inp) returns (Out);
}

message Inp{
  string name = 1;
}

message Out{
  string text = 1;
}
```

Here's what a day to day workflow should look like.
```bash
~/Desktop via py v3.11.6 (base)
> tree
.
└── rpc
    └── greet.proto

2 directories, 1 file

~/Desktop via py v3.11.6 (base)
> cd rpc/

~/Desktop/rpc via py v3.11.6 (base)
> create_grpc_service -f greet.proto -c yes
path: greet.proto
pb_path: /home/ashu/venvs/base/lib/python3.11/site-packages/grpc_assets/greet
Generating Server Code...
Parsing protobuf...
Parsed protobuf: [
  {
    "name": "Greet",
    "methods": [
      "hi",
      "bye"
    ]
  }
]
Adding service: Greet
Adding method: hi
Adding method: bye
Generating Client Code...
Parsing protobuf...
Parsed protobuf: [
  {
    "name": "Greet",
    "methods": [
      "hi",
      "bye"
    ]
  }
]
Adding service: Greet
Adding method: hi
Adding method: bye
```


This generates, two things... one service class and a test case, like so...

```bash
~/Desktop via py v3.11.6 (base)
> tree rpc/
rpc/
├── greet.proto
├── greet.py
└── tests
    └── test_greet.py

2 directories, 3 files
```

service

```python
from grpc_assets.greet import greet_pb2
from grpc_assets.greet.greet_pb2_grpc import GreetServicer

"""
Proto
syntax = "proto3";

service Greet{
    rpc hi(Inp) returns (Out);
    rpc bye(Inp) returns (Out);
}

message Inp{
  string name = 1;
}

message Out{
  string text = 1;
}

"""


class GreetService(GreetServicer):
    def hi(self, context):
        """
        # TODO: add inputs as per proto
        # TODO: add logic and return output as per proto
        """
        return

    def bye(self, context):
        """
        # TODO: add inputs as per proto
        # TODO: add logic and return output as per proto
        """
        return
```

testcase 

```python
from grpc_assets.stub import get_stub
import grpc_assets.greet.greet_pb2 as pb2
from unittest import TestCase


"""
Proto
syntax = "proto3";

service Greet{
    rpc hi(Inp) returns (Out);
    rpc bye(Inp) returns (Out);
}

message Inp{
  string name = 1;
}

message Out{
  string text = 1;
}

"""


class GreetClientTestCase(TestCase):
    stub = get_stub("greet")

    def test_hi(self):
        # stub.<your rpc method>(pb2.<your proto message>(params))
        ...

    def test_bye(self):
        # stub.<your rpc method>(pb2.<your proto message>(params))
        ...
```

Then all I have to do is implement the methods...

Service 

```python
class GreetService(GreetServicer):
    def hi(self, inp, context):
        print(f"req: {inp}")
        return greet_pb2.Out(text=f"Hi {inp.name}")

    def bye(self, inp, context):
        print(f"req: {inp}")
        return greet_pb2.Out(text=f"Bye {inp.name}")
```

Testcase

```python
class GreetClientTestCase(TestCase):
    stub = get_stub("greet")

    def test_hi(self):
        print(self.stub.hi(pb2.Inp(name="Ashu")))

    def test_bye(self):
        print(self.stub.bye(pb2.Inp(name="Ashu")))
```

That's it, then I should be able to call the service like so...

server 
```bash
~/Desktop via py v3.11.6 (base)
x export GRPC_PORT=50001

~/Desktop via py v3.11.6 (base)
> servegrpc
/home/ashu/venvs/base/bin/servegrpc:21: PydanticDeprecatedSince20: `pydantic.config.Extra` is deprecated, use literal values instead (e.g. `extra='allow'`). Deprecated in Pydantic V2.0 to be removed in V3.0. See Pydantic V2 Migration Guide at https://errors.pydantic.dev/2.3/migration/
  extra = Extra.ignore
starting grpc server...
req: name: "Ashu"

req: name: "Ashu"
```

client
```bash
> python3 -m unittest rpc.tests.test_greet
text: "Bye Ashu"

.text: "Hi Ashu"

.
----------------------------------------------------------------------
Ran 2 tests in 0.006s

OK
```

Note, here, I'm storing the protoc generated pb2 files under a package called grpc_assets under site-packages.
Also,  there's one catch, the code gen logic I wrote has one retriction, proto file name needs to match the main service name, which limits the number of services to 1. 

This can always be improved upon.

