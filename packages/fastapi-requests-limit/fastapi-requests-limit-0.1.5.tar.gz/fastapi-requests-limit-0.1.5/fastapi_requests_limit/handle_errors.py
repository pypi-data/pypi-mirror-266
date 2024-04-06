class EngineException(Exception):
    def __init__(self, expression, message):
        self.message = message
        self.expression = expression


class NotConfigException(Exception):
    def __init__(self):
        self.message = """Please ensure to initialize the Limiter with a storage engine option in your main FastAPI 
                application file. For example: Limiter(storage_engine="memory") or Limiter(storage_engine="redis"). """
        self.expression = "The Limiter configuration has not been initialized."
