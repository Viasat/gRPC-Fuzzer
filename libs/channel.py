import grpc

def create_client_channel(hostname):
    channel = grpc.insecure_channel(
        hostname
    )
    return channel
