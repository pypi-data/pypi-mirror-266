import grpc

class RateLimitError(grpc.RpcError):
    pass

class AuthenticationError(grpc.RpcError):
    pass

class InternalServerError(grpc.RpcError):
    pass

class TimeoutError(grpc.RpcError):
    pass

class ServiceUnavailableError(grpc.RpcError):
    pass

def translate_grpc_error(e: grpc.RpcError) -> grpc.RpcError:
    """
    Translate a gRPC error into a more specific exception
    """
    if not isinstance(e, grpc.RpcError):
        return e

    if e.code() == grpc.StatusCode.UNAUTHENTICATED:
        return AuthenticationError(e)
    elif e.code() == grpc.StatusCode.PERMISSION_DENIED:
        return AuthenticationError(e)
    elif e.code() == grpc.StatusCode.RESOURCE_EXHAUSTED:
        return RateLimitError(e)
    elif e.code() == grpc.StatusCode.INTERNAL:
        return InternalServerError(e)
    elif e.code() == grpc.StatusCode.DEADLINE_EXCEEDED:
        return TimeoutError(e)
    elif e.code() == grpc.StatusCode.UNAVAILABLE:
        return ServiceUnavailableError(e)
    elif e.code() == grpc.StatusCode.UNKNOWN:
        return ServiceUnavailableError(e)
    elif e.code() == grpc.StatusCode.UNIMPLEMENTED:
        return ServiceUnavailableError(e)
    else:
        return e
