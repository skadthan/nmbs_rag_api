
from pydantic import BaseModel,EmailStr
from typing import List
# Models
class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    date_of_birth: str
    password: str
    requested_roles: List[str]

class RoleApproval(BaseModel):
    request_id: str
    status: str  # "approved" or "rejected"