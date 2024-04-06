def get_redis_storage():
    from fastapi_requests_limit.storages.redis import RedisStorage
    return RedisStorage

def get_memory_store():
    from fastapi_requests_limit.storages.memory import MemoryStorage
    return MemoryStorage

storage_engines = {"redis": get_redis_storage, "memory": get_memory_store}


def get_engines_availables():
    return storage_engines.keys()
