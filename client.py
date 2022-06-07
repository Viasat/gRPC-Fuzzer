import grpc
import logging
import os
from libs.channel import create_client_channel
from fuzzers.hello_world import HelloWorldFuzzer

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
        fuzzer = HelloWorldFuzzer(self.hostname, self.metadata, logger)
        fuzzer.hello_world()
        fuzzer.write_junit_report()

def main():
    client = Client()
    client.run_hello_world_fuzzer()

if __name__ == '__main__':
    main()
