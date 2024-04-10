from typing import List, Optional
from pydantic import BaseModel
from typing import List

from scale_egp.utils.model_utils import BaseModel


class Account(BaseModel):
    id: str
    name: str


class UserRole(BaseModel):
    role: str
    account: Account


class UserInfoResponse(BaseModel):
    id: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: str
    accounts: List[UserRole]
