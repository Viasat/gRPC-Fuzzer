import asyncio
import datetime
import grpc
import os
from junit_xml import TestSuite, TestCase
from libs.helpers import max_concurrent
from libs.req_info import ReqInfo
from protofuzz import protofuzz

TIMEOUT=15

class DefaultFuzzer:# TODO create handler multiple requests
    def __init__(self, hostname, metadata, logger, req_info: ReqInfo):
        self.hostname = hostname
        self.metadata = metadata
        self.logger = logger
        self.test_cases = []
        self.req_info = req_info

    async def fuzzer_task(self, obj) -> None:
        async with grpc.aio.insecure_channel(self.hostname) as channel:
            stub = getattr(self.req_info.pb2_grpc_class, self.req_info.stub_name)(channel=channel)
            proto_name_values = {}
            for attr in dir(obj): # TODO: make sure this works with nested objects
                if attr != "Extensions" and attr != "DESCRIPTOR" and not attr.startswith("_") and not callable(getattr(obj, attr)):
                    proto_name_values[attr] = getattr(obj,attr)
            request = getattr(self.req_info.pb2_class, self.req_info.request_name)(**proto_name_values)
            try:
                response = await getattr(stub,self.req_info.function_name)(
                    request=request,
                    metadata=self.metadata,
                    timeout=TIMEOUT
                )
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED or rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    self.logger.info('%s,%s', self.req_info.request_name, request)
                    tc = TestCase(self.req_info.request_name, self.req_info.function_name, TIMEOUT, '', '', None, datetime.datetime.now().isoformat())
                    tc.add_failure_info(request)
                    self.test_cases.append(tc)
                    if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                        print("The server has crashed")
                        raise

    async def fuzzer_producer(self):
        cwd = os.getcwd()
        include_path = cwd + self.req_info.proto_info.proto_path
        proto_file = cwd + self.req_info.proto_info.proto_path + self.req_info.proto_info.proto_name
        message_fuzzers = protofuzz.from_file(include_path, proto_file)
        for obj in message_fuzzers[self.req_info.request_name].permute():
            yield self.fuzzer_task(obj)

    def start_fuzzer(self):
        print("Start fuzzing " + self.req_info.request_name)
        asyncio.run(max_concurrent(150, self.fuzzer_producer()))
        print("Done fuzzing " + self.req_info.request_name)

    def write_junit_report(self):
        tc = TestCase(self.req_info.request_name + ' Successfully Finished', self.req_info.function_name, TIMEOUT, 'Success', '')
        self.test_cases.append(tc)
        ts = TestSuite(self.req_info.request_name + " Fuzzing Suite", self.test_cases)
        cwd = os.getcwd()
        with open(cwd+'/logs/' + self.req_info.request_name + '.xml', 'w') as f:
            TestSuite.to_file(f, [ts], prettyprint=False)
