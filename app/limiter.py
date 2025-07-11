from slowapi import Limiter
from slowapi.util import get_remote_address
import os

redis_host = os.getenv("REDIS_HOST", "localhost")
redis_port = os.getenv("REDIS_PORT", "6379")  
redis_uri = f"redis://{redis_host}:{redis_port}"

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=redis_uri
)
