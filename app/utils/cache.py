import redis.asyncio as redis
import json
import os
from dotenv import load_dotenv
from typing import Optional,Any
load_dotenv()

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    db=int(os.getenv("REDIS_DB")),
    decode_responses=True
)

async def get_cache(key: str)-> Optional[Any]:
    try:
        data = await redis_client.get(key)
        if data:
            return json.loads(data) 
    except Exception as e:
        print(f"[Redis Get Error] Key: {key} | Data: {data} | Error: {e}")


    return None

async def set_cache(key: str, value: Any, expire: int = 300)-> None:
    try:
        await redis_client.set(key, json.dumps(value), ex=expire)
    except Exception as e:
         print(f"[Redis Set Debug] Key: {key} | Value: {value}")

async def delete_cache(key: str):
    try:
        await redis_client.delete(key)
    
    except Exception as e:
         print(f"[Redis delete Error] Key: {key}| Error:{e}")

