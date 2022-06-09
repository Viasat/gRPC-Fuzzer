import asyncio
import datetime
import grpc
import os
from junit_xml import TestSuite, TestCase
from libs.helpers import max_concurrent
from libs.pb2_modules import PB2Modules
from libs.req_info import ReqInfo
from google.protobuf.json_format import MessageToDict

TIMEOUT=15

'''
    Fuzzes a single grpc request.
'''
class DefaultFuzzer:
    def __init__(self, hostname, metadata, logger, modules: PB2Modules, message_fuzzers, req_info: ReqInfo):
        self.hostname = hostname
        self.metadata = metadata
        self.logger = logger
        self.test_cases = []
        self.req_info = req_info
        self.modules = modules
        self.message_fuzzers = message_fuzzers

    '''
        Given the payload from protofuzz, make the grpc call and check if the server crashes or times out indicating a thread crash.
    '''
    async def fuzzer_task(self, obj) -> None:
        async with grpc.aio.insecure_channel(self.hostname) as channel:
            stub = getattr(self.modules.pb2_grpc, self.req_info.stub_name)(channel=channel)            
            proto_as_dict = MessageToDict(obj) # TODO: make sure this works with nested objects
            request_payload = getattr(self.modules.pb2, self.req_info.request_input_name)(**proto_as_dict)
            try:
                response = await getattr(stub, self.req_info.request_name)(
                    request=request_payload,
                    metadata=self.metadata,
                    timeout=TIMEOUT
                )
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.DEADLINE_EXCEEDED or rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    self.logger.info('%s,%s', self.req_info.request_name, request_payload)
                    tc = TestCase(self.req_info.request_input_name, self.req_info.request_name, TIMEOUT, '', '', None, datetime.datetime.now().isoformat())
                    tc.add_failure_info(request_payload)
                    self.test_cases.append(tc)
                    if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                        print("The server has crashed")
                        raise Exception("Server Crashed")

    '''
        Uses the linear method in protofuzz to generate payloads.
        This can be switched to permute for more coverage.
        Please refer to protofuzz documentation.
    '''
    async def fuzzer_producer(self):
        for obj in self.message_fuzzers[self.req_info.request_input_name].linear():
            yield self.fuzzer_task(obj)

    '''
        Start the fuzzer concurrently to speed up the process.
    '''
    def start_fuzzer(self):
        print("Start fuzzing " + self.req_info.request_name)
        try:
            asyncio.run(max_concurrent(150, self.fuzzer_producer()))
        except Exception as e:
            self.write_junit_report()
            exit()
        print("Done fuzzing " + self.req_info.request_name)

    '''
        Publishes a junit report which is good for jenkins.
    '''
    def write_junit_report(self):
        tc = TestCase(self.req_info.request_name + ' Finished', self.req_info.request_name, TIMEOUT, '', '')
        self.test_cases.append(tc)
        ts = TestSuite(self.req_info.request_name + " Fuzzing Suite", self.test_cases)
        cwd = os.getcwd()
        with open(cwd+'/logs/' + self.req_info.request_name + '.xml', 'w') as f:
            TestSuite.to_file(f, [ts], prettyprint=False)
