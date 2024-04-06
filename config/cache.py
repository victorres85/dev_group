from aiocache import Cache, caches
from aiocache.serializers import PickleSerializer
from fastapi.responses import JSONResponse
from config.logger import logger 


# Initialize Redis cache
CACHE = Cache(Cache.REDIS, endpoint="localhost", port=6379, serializer=PickleSerializer())

# Exception handler for aiocache errors
async def cache_error_handler(request, exc):
    logger.error(f"Cache error: {str(exc)}")


async def clear_cache(cache_name: str):
    try:
        exists = await CACHE.exists(cache_name)
        if exists:
            await CACHE.delete(cache_name)
            logger.info(f"Cache {cache_name} cleared successfully")
    except Exception as e:
       logger.error(f"Cache error: {str(e)}")


async def update_cache(cache_name: str, fn: callable):
    try:
        exists = await CACHE.exists(cache_name)
        if exists:
            await CACHE.delete(cache_name)
        await fn()
        logger.info(f"Cache {cache_name} updated successfully")
        return JSONResponse(content={"message": "Cache cleared successfully"}, status_code=200)
    except Exception as e:
       logger.error(f"Error updating Cache: {str(e)}")

# fucntion to retrieve cache data
async def get_cache_data(cache_name: str, fn: callable):
    try:
        exists = await CACHE.exists(cache_name)
        if exists:
            data = await CACHE.get(cache_name)
            return data
        else:
            data = await fn()
            await CACHE.set(cache_name, data, ttl=3600)
            return data
    except Exception as e:
        logger.error(f"Cache error: {str(e)}")
        return None
    
async def add_cache_data(key: str, field_data_func: callable):
    cached_data = await CACHE.get(key)
    if not cached_data:
        cached_data = field_data_func()
        await CACHE.set(key, cached_data)
    return cached_data