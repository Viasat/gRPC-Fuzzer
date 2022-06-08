from libs.class_info import ClassInfo
from libs.proto_info import ProtoInfo
from pydoc import locate
import sys

class ReqInfo:
    def __init__(self, class_info: ClassInfo, proto_info: ProtoInfo, stub_name, request_name, function_name):
        print(class_info.class_path+class_info.pb2)
        sys.path.append("./" + class_info.class_path.replace(".","/"))
        self.pb2_class = locate(class_info.class_path+'.'+class_info.pb2)
        self.pb2_grpc_class = locate(class_info.class_path+'.'+class_info.pb2_grpc)
        self.proto_info = proto_info
        self.stub_name = stub_name
        self.request_name = request_name
        self.function_name = function_name
