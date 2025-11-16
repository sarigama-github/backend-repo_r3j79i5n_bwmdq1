from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class Contact(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    message: str = Field(..., min_length=5, max_length=2000)

class EmailLog(BaseModel):
    to: EmailStr
    subject: str
    status: str
    error: Optional[str] = None
