from .collection import Collection

class Client:
    def __init__(self):
        self._collections = []

    def create_collection(self, name: str) -> Collection:
        collection = Collection(name)
        self._collections.append(collection)
        return collection
