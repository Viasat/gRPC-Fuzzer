import logging
import grpc
from compiled_proto.hello_world import helloworld_pb2, helloworld_pb2_grpc
from protofuzz import protofuzz
import os
import asyncio
from junit_xml import TestSuite, TestCase
from libs.helpers import max_concurrent
import datetime

TIMEOUT=15

class HelloWorldFuzzer:
    def __init__(self, hostname, metadata, logger):
        self.hostname = hostname
        self.metadata = metadata
        self.logger = logger
        self.test_cases = []

    async def hello_world_task(self, obj) -> None:
        async with grpc.aio.insecure_channel(self.hostname) as channel:
            stub = helloworld_pb2_grpc.GreeterStub(channel=channel)
            request = helloworld_pb2.HelloRequest(name=obj.name)
            try:
#                print(obj.name, end="", flush=True)
                response = await stub.SayHello(
                    request=request,
                    metadata=self.metadata,
                    timeout=TIMEOUT
                )
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED or rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    self.logger.info('HelloRequest,%s', request)
                    tc = TestCase('HelloRequest', "HelloWorldFuzzer", TIMEOUT, '', '', None, datetime.datetime.now().isoformat())
                    tc.add_failure_info(request)
                    self.test_cases.append(tc)
                    if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                        print("The server has crashed")
                        raise

    async def hello_world_producer(self):
        cwd = os.getcwd()
        include_path = cwd + "/dependencies/vulnerable-grpc-example/protos"
        proto_file = cwd + "/dependencies/vulnerable-grpc-example/protos/helloworld.proto"
        message_fuzzers = protofuzz.from_file(include_path, proto_file)
        for obj in message_fuzzers['HelloRequest'].permute():
            yield self.hello_world_task(obj)

    def hello_world(self):
        print("Start fuzzing HelloWorld")
        asyncio.run(max_concurrent(150, self.hello_world_producer()))
        print("Done fuzzing HelloWorld")

    def write_junit_report(self):
        tc = TestCase('Hello World Successfully Finished', "hello_world", TIMEOUT, 'Success', '')
        self.test_cases.append(tc)
        ts = TestSuite("Hello World Fuzzing Suite", self.test_cases)
        cwd = os.getcwd()
        with open(cwd+'/logs/hello_world.xml', 'w') as f:
            TestSuite.to_file(f, [ts], prettyprint=False)
