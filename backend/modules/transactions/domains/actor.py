class ActorDomain:
    def __init__(self, name: str = None, id: int = None, created_at: str = None, updated_at: str = None):
        self.name = name
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at

    def update(self, name: str):
        self.name = name
