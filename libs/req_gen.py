from libs.pb2_modules import PB2Modules
from libs.req_info import ReqInfo

'''
    Given modules can parse them and find all requests.
'''
class ReqGen:
    def __init__(self, modules: PB2Modules):
        self.modules = modules

    '''
        Parse the modules and create a list of ReqInfo for the fuzzer to use.
    '''
    def gen(self):
        req_infos = []
        service_tuple_array = getattr(getattr(getattr(self.modules.pb2, 'DESCRIPTOR'),'services_by_name'),'items')()
        for service in service_tuple_array:
            stub_name = service[0]+"Stub" # first item in tuple is the name, protoc adds stub to the name
            for request in service[1].methods: # second item in tuple is the ServiceDescriptor class .methods are requests like SayHello, input_type is like HelloRequest proto
                request_name = request.name
                request_input_name = request.input_type.name
                req_infos.append(ReqInfo(stub_name,request_name,request_input_name))
        return req_infos
