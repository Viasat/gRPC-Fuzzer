import os

'''
    Contains the necessary filepaths for protofuzz/ protoc to generate grpc python proto files.
'''
class ProtoInfo:
    def __init__(self, include_path, proto_name):
        cwd = os.getcwd()
        include_path = cwd + "/" + include_path
        proto_path = include_path + proto_name
        self.include_path = include_path
        self.proto_path = proto_path

    #TODO: validations
        