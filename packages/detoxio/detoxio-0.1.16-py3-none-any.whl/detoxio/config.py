import os

def get_api_host() -> str:
    return "api.detoxio.ai"

def get_api_port() -> int:
    return 443

def debug() -> bool:
    return os.environ.get("DETOXIO_DEBUG", "false").lower() == "true"

def get_api_key_env_name() -> str:
    return "DETOXIO_API_KEY"

def load_key_from_env():
    """
    Load the detoxio.ai API key from the environment.
    Throws a ValueError if the key is not found.
    """
    key_name = get_api_key_env_name()
    key = os.environ.get(key_name)
    if key is None:
        raise ValueError(f"{key_name} is not set in the environment")

    return key

