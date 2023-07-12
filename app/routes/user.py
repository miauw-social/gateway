from fastapi import APIRouter
from argon2 import hash_password
from rabbit.rabbit import r
import secrets
userRouter = APIRouter(prefix="/users", tags=["users"])


@userRouter.post("/", response_model=UserSchema, description="create user")
async def create_user(user_data: UserCreate):
    pass



@userRouter.get("/")
async def test():
    print("[!] before")
    body = await r.call("user.create", {"test": 1})
    print("[!] after")
    print(body)
    return ""
    

@userRouter.get("/{user_id}", description="get user by id")
async def get_user_by_id(user_id: str):
    print(user)