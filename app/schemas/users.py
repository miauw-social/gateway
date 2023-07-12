import pydantic
import datetime

class UserCreate(pydantic.BaseModel):
    username: str
    email: pydantic.EmailStr
    password: str


class User(pydantic.BaseModel):
    username: str
    email: pydantic.EmailStr
    created_at: datetime.datetime
    modified_at: datetime.datetime

