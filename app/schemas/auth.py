from pydantic import BaseModel, EmailStr

class LoginDataUsername(BaseModel):
    username: str
    password: str

class LoginDataEmail(BaseModel):
    email: EmailStr
    password: str
