from .handle_errors import EngineException, NotConfigException
from .storage_engines import get_engines_availables, storage_engines


class Limiter:
    _instancia = None

    def __new__(cls, *args, **kwargs):
        if cls._instancia is None:
            cls._instancia = super(Limiter, cls).__new__(cls)
            cls._instancia.init(*args, **kwargs)
        return cls._instancia

    def init(self, storage_engine=False, **storage_params):
        if not storage_engine:
            raise NotConfigException()
        if storage_engine not in get_engines_availables():
            raise EngineException(
                "engine error", f"not exits the engine {storage_engine} connection"
            )
        self.storage_engine = storage_engine
        self.storage = storage_engines.get(storage_engine, "memory")()(**storage_params)
