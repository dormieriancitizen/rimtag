import logging, json, asyncio
from aiofile import async_open

async def update_json_cache(cache_path,new):
    logger = logging.getLogger()

    # Load cached data if it exists
    if cache_path.exists():
        try:
            with open(cache_path, "r") as cache_file:
                cached_steamd = json.load(cache_file)
                cached_steamd.update(new)  # Merge new data with cached data
        except Exception as e:
            logger.warning(f"Error reading from cache: {e}")
    
    try:
        async with async_open(cache_path, "w") as cache_file:
            data = json.dumps(new, indent=4)
            asyncio.create_task(cache_file.write(data))
    except Exception as e:
        logger.warning(f"Error writing to cache: {e}")