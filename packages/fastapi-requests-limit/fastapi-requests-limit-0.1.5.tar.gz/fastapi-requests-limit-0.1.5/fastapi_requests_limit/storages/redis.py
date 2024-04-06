import redis

from .storage import Storage


class RedisStorage(Storage):
    def __init__(self, host, port):
        self.storage_engine = self._create_connection(host, port)
        super().__init__()

    def _create_connection(self, host, port):
        return redis.Redis(host=host, port=port, decode_responses=True)

    def create_register(self, id: str) -> None:
        register = self.create_first_register()
        self.storage_engine.hset(id, mapping=register)

    def update_register(self, id: str, data: dict):
        register = self.register
        if not register:
            register = self.get_register(id)
        register.update(data)
        self.storage_engine.hset(id, mapping=register)

    def get_register(self, id: str) -> dict:
        register = self.storage_engine.hgetall(id)
        self.register = register
        return register
