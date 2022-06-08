import grpc
import logging
import os
from libs.channel import create_client_channel
from fuzzers.default_fuzzer import DefaultFuzzer
from libs.class_info import ClassInfo
from libs.proto_info import ProtoInfo
from libs.req_info import ReqInfo

class FilterNewLines(logging.Filter):
    def filter(self, record):
        record.msg = record.msg.replace('\n','').replace('\r','')
        return record

def setup_logger(logger_name, log_file, level=logging.INFO):
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s : %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    file_handler = logging.FileHandler(log_file, mode='w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    logger.addFilter(FilterNewLines())
    logger.setLevel(level)
    logger.addHandler(file_handler)


class Client:
    metadata = None
    hostname = 'localhost:50051'

    def __init__(self):
        self.authenticate()

    def authenticate(self):
        # Call your authentication grpc and set metadata or client data here. depends on authentication method
        return

    def run_hello_world_fuzzer(self):
        setup_logger('HelloWorldLog', 'logs/hello_world.log')
        logger = logging.getLogger('HelloWorldLog')
        class_info = ClassInfo('compiled_proto.hello_world', 'helloworld_pb2', 'helloworld_pb2_grpc')
        proto_info = ProtoInfo('/dependencies/vulnerable-grpc-example/protos/', 'helloworld.proto')
        req_info = ReqInfo(class_info, proto_info, 'GreeterStub', 'HelloRequest', 'SayHello')
        fuzzer = DefaultFuzzer(self.hostname, self.metadata, logger, req_info)
        fuzzer.start_fuzzer()
        fuzzer.write_junit_report()

def main():
    client = Client()
    client.run_hello_world_fuzzer()

if __name__ == '__main__':
    main()
