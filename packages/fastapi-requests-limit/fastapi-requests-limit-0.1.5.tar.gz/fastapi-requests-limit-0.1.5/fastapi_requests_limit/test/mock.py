class RedisMock:
    def __init__(self):
        print("entro 0")
        self.data = {}

    def hset(self, id, mapping):
        print("entro 1")
        self.data[id] = mapping

    def hgetall(self, id):
        print("entro 2")
        return self.data.get(id, {})
