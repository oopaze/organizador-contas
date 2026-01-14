from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.userdata.domains.user import UserDomain


class ProfileDomain:
    def __init__(
        self, 
        bio: str = "", 
        salary: float = 0.0, 
        first_name: str = "", 
        last_name: str = "", 
        user_id: int = None,
        id: int = None, 
        created_at: str = None, 
        updated_at: str = None, 
    ):
        self.bio = bio
        self.salary = salary
        self.first_name = first_name
        self.last_name = last_name
        self.user_id = user_id
        self.id = id
        self.created_at = created_at
        self.updated_at = updated_at

    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    def update(self, data: dict):
        self.bio = data.get("bio", self.bio)
        self.salary = data.get("salary", self.salary)
        self.first_name = data.get("first_name", self.first_name)
        self.last_name = data.get("last_name", self.last_name)
