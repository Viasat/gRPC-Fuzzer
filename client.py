import argparse
import logging
import os
from protofuzz import protofuzz
from fuzzers.default_fuzzer import DefaultFuzzer
from libs.pb2_modules import PB2Modules
from libs.proto_info import ProtoInfo
from libs.req_gen import ReqGen

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
        Call your authentication grpc and set metadata or client data here.
        Depends on authentication method.
        If you are using client certs, you will need to setup a local proxy like nginx.
    '''
    def authenticate(self):
        return


    '''
        Compiles the proto using protofuzz, which also returns a dictionary:
            {proto_object_name: protofuzz.protofuzz.ProtobufGenerator}
        Protofuzz also puts the generated grpc python proto files which is
            symlinked in compiled_proto/tmp
        Load the modules into the program using PB2Modules

        Return the dictionary and the modules.
    '''
    def load_modules(self, proto_info):
        message_fuzzers, pb2_path = protofuzz.from_file(proto_info.include_path,
                                                        proto_info.proto_path)

        pb2_python_module_name = os.path.splitext(os.path.basename(pb2_path))[0]
        pb2_grpc_python_module_name = pb2_python_module_name + "_grpc"
        pb2_python_module_path = ("compiled_proto" + os.path.dirname(pb2_path)).replace("/", ".")

        modules = PB2Modules(pb2_python_module_path, pb2_python_module_name,
                             pb2_grpc_python_module_name)
        return modules, message_fuzzers

    '''
        Parse the grpc python proto files and grab all of the stubs, requests,
        and inputs to those requests.

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
            fuzzer = DefaultFuzzer(self.hostname, self.metadata, logger,
                                   modules, message_fuzzers, req_info)
            fuzzer.start_fuzzer()
            fuzzer.write_junit_report()

def main(args):
    # Pass me the proto file and I'll compile and fuzz all the requests in it.
    client = Client()
    for proto in args.protos:
        proto_info = ProtoInfo(args.include_path, proto)
        client.run_fuzzer(proto_info)    
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Uses protofuzz to send payloads to \
        gRPC endpoints described in .proto files passed in \
        using -I and -p",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-I", "--include-path", help="The directory where the protos are stored. \
        Note this must point to the common ancestor of the protos.  So if a proto references a \
        proto in the aunt's directory, then this must point to the grandparent directory. \
        Otherwise if it does not reference a non-sibling proto then this is just the directory the \
        proto is stored in (parent).",
        default="dependencies/vulnerable-grpc-example/protos/")
    parser.add_argument("-p", "--protos", help="The name of the proto file(s).  This can also be a \
        comma seperated list.",
        default="helloworld.proto")
    args = parser.parse_args()
    args.protos = args.protos.replace(" ", "")
    args.protos = args.protos.split(",")
    main(args)
