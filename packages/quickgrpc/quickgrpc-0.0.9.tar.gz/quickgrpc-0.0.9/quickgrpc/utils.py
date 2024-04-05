import importlib
import json
import sys
import re


from typing import Callable

import grpc

from pydantic import Extra
from pydantic_settings import BaseSettings


def add_grpc_service(name, server):
    sys.path.append(".")
    module = importlib.import_module(f"rpc.{name}")
    service = getattr(module, f"{name.title()}Service")()
    service_grpc = importlib.import_module(f"grpc_assets.{name}.{name}_pb2_grpc")
    getattr(service_grpc, f"add_{name.title()}Servicer_to_server")(service, server)


def parse_proto_get_services(proto_file_path):
    print("Parsing protobuf...")

    services = []
    with open(proto_file_path, "r") as f:
        proto_data = f.read()

    service_pattern = r"service\s+(\w+)\s*{((?:\s*rpc\s+(\w+)\s*\(.*?\);)+)\s*}"
    matches = re.findall(service_pattern, proto_data, re.DOTALL)

    for match in matches:
        service_name = match[0]
        rpc_methods = match[1]
        method_matches = re.findall(r"rpc\s+(\w+)\s*\(.*?\);", rpc_methods)

        service_info = {"name": service_name, "methods": method_matches}
        services.append(service_info)

    print(f"Parsed protobuf: {json.dumps(services, indent=2)}")
    return services


class ServerConfig(BaseSettings):
    grpc_port: int

    class config:
        extra = Extra.ignore


settings = ServerConfig()


def get_stub(service, host: str = None, port: int = None) -> Callable:
    if not host:
        host = "localhost"
    if not port:
        port = settings.grpc_port

    # instantiate a channel
    channel = grpc.insecure_channel(f"{host}:{port}")
    pb2_grpc = importlib.import_module(f"grpc_assets.{service}.{service}_pb2_grpc")
    # bind the client and the server
    stub = getattr(pb2_grpc, f"{service.title()}Stub")(channel)
    return stub
