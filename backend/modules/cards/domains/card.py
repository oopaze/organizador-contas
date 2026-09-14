class CardDomain:
    def __init__(
        self,
        name: str = None,
        due_day: int = 1,
        is_active: bool = True,
        id: int = None,
        user_id: int = None,
        created_at: str = None,
        updated_at: str = None,
        deleted_at: str = None,
    ):
        self.name = name
        self.due_day = due_day
        self.is_active = is_active
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.updated_at = updated_at
        self.deleted_at = deleted_at

    def update(self, data: dict):
        self.name = data.get("name", self.name)
        self.due_day = data.get("due_day", self.due_day)
        self.is_active = data.get("is_active", self.is_active)
