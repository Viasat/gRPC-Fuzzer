from pydoc import locate
import sys

'''
    Loads the grpc python proto modules into memory.
'''
class PB2Modules:
    def __init__(self, pb2_python_module_path, pb2_python_module_name, pb2_grpc_python_module_name):
        sys.path.append("./" + pb2_python_module_path.replace(".","/"))
        self.pb2 = locate(pb2_python_module_path+'.'+pb2_python_module_name)
        self.pb2_grpc = locate(pb2_python_module_path+'.'+pb2_grpc_python_module_name)
