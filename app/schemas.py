from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class ExpAction(BaseModel):
    id: Optional[int] = None
    name: str
    role: Optional[str] = None
    repeatable: bool = True
    exp_value: int = 10
    description: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class UserExperience(BaseModel):
    id: Optional[int] = None
    user_id: int
    role: Optional[str] = None
    total_exp: int = 0
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class ExpTransaction(BaseModel):
    id: Optional[int] = None
    user_experience_id: int
    user_id: int
    action_id: int
    exp_awarded: int
    reference: Optional[int] = None
    created_at: Optional[datetime] = None

    class Config:
        orm_mode = True
