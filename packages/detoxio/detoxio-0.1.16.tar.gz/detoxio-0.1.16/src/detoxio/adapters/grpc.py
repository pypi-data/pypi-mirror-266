import grpc

def get_secure_channel_with_token(host: str, port: int, token: str) -> grpc.Channel:
    credential = grpc.access_token_call_credentials(token)
    channel = grpc.secure_channel(f'{host}:{port}',
        grpc.composite_channel_credentials(grpc.ssl_channel_credentials(), credential))

    return channel

