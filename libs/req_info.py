'''
    The necessary information to create a grpc call.
    Example: GreeterStub, SayHello, HelloRequest
'''
class ReqInfo:
    def __init__(self, stub_name, request_name, request_input_name):
        self.stub_name = stub_name
        self.request_name = request_name
        self.request_input_name = request_input_name
