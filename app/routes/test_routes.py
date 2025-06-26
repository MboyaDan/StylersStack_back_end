from fastapi import APIRouter, Request
from app.utils.cache import set_cache, get_cache
from app.limiter import limiter 
import os
router = APIRouter(prefix="/test", tags=["Test"])

@router.get("/cache", include_in_schema=False)
@limiter.limit(os.getenv("RATE_LIMIT"))
async def test_redis_cache(request: Request):  
    await set_cache("ping", {"hello": "stylerstack"}, expire=60)
    cached = await get_cache("ping")
    return cached
