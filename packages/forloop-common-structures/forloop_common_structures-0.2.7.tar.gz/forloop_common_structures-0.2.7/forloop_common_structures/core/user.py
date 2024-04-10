from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    email: str
    auth0_subject_id: str
    given_name: str
    family_name: str
    picture_url: str
    uid: Optional[str] = None