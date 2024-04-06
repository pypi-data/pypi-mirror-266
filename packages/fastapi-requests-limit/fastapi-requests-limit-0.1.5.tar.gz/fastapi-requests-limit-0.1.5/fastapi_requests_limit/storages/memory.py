from .storage import Storage

count = {}


class MemoryStorage(Storage):
    def __init__(self):
        self.storage_engine = count
        super().__init__()

    def create_register(self, id: str) -> None:
        register = self.create_first_register()
        self.storage_engine[id] = register

    def update_register(self, id: str, data: dict):
        register = self.register
        if not register:
            register = self.get_register(id)
        register.update(data)

    def get_register(self, id: str) -> dict:
        print(self.storage_engine)
        register = self.storage_engine.get(id, {})
        self.register = register
        return register.copy()

    @classmethod
    def clear(cls):
        count.clear()
