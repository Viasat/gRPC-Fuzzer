import logging
import os
from fuzzers.default_fuzzer import DefaultFuzzer
from libs.pb2_modules import PB2Modules
from libs.proto_info import ProtoInfo
from libs.req_gen import ReqGen
from protofuzz import protofuzz

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

    '''
        Call your authentication grpc and set metadata or client data here. Depends on authentication method.
    '''
    def authenticate(self):
        return
        

    '''
        Compiles the proto using protofuzz, which also returns a dictionary {proto_object_name: protofuzz.protofuzz.ProtobufGenerator}
        Protofuzz also puts the generated grpc python proto files which is symlinked in compiled_proto/tmp
        Load the modules into the program using PB2Modules

        Return the dictionary and the modules.
    '''
    def load_modules(self, proto_info):
        message_fuzzers, pb2_path = protofuzz.from_file(proto_info.include_path, proto_info.proto_path)

        pb2_python_module_name = os.path.splitext(os.path.basename(pb2_path))[0]
        pb2_grpc_python_module_name = pb2_python_module_name + "_grpc"
        pb2_python_module_path = ("compiled_proto" + os.path.dirname(pb2_path)).replace("/", ".")

        modules = PB2Modules(pb2_python_module_path, pb2_python_module_name, pb2_grpc_python_module_name)
        return modules, message_fuzzers

    '''
        Parse the grpc python proto files and grab all of the stubs, requests, and inputs to those requests.

        Return a list of that information.
    '''
    def generate_requests(self, modules):
        req_generator = ReqGen(modules)
        req_infos = req_generator.gen()
        return req_infos

    '''
        Sets up the plaintext log.
        Loads the python grpc modules.  
        Generates necessary request metadata and calls a fuzzer for each request defined.
        Writes the junit report log.
    '''
    def run_fuzzer(self, proto_info: ProtoInfo):
        log_name = os.path.basename(proto_info.proto_path).replace(".proto", "")
        setup_logger(log_name, './logs/'+log_name+'.log')
        logger = logging.getLogger(log_name)

        modules, message_fuzzers = self.load_modules(proto_info)
        req_infos = self.generate_requests(modules)
        for req_info in req_infos:
            fuzzer = DefaultFuzzer(self.hostname, self.metadata, logger, modules, message_fuzzers, req_info)
            fuzzer.start_fuzzer()
            fuzzer.write_junit_report()

def main():
    # Pass me the proto file and I'll compile and fuzz all the requests in it. Note that a new Client is needed for every proto file.
    client = Client()
    proto_info = ProtoInfo('/dependencies/vulnerable-grpc-example/protos/', 'helloworld.proto')
    client.run_fuzzer(proto_info)
    

if __name__ == '__main__':
    main()
