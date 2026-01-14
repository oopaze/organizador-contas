from datetime import datetime
from typing import Optional

from modules.userdata.domains.profile import ProfileDomain


class UserDomain:
    def __init__(
        self,
        email: str,
        is_active: bool = True,
        is_staff: bool = False,
        is_superuser: bool = False,
        id: Optional[int] = None,
        profile: Optional["ProfileDomain"] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.email = email
        self.is_active = is_active
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.profile = profile
        self.created_at = created_at
        self.updated_at = updated_at
