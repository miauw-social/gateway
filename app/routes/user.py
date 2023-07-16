from fastapi import APIRouter, BackgroundTasks
from argon2 import hash_password
from schemas.users import User, UserCreate
from utils.rabbit import mayor, emailer
from utils.enums import EmailTypes



userRouter = APIRouter(prefix="/users", tags=["users"])


@userRouter.post("/", description="create user")
async def create_user(user: UserCreate, bg:BackgroundTasks):
    vid, user_profile = await mayor.create(user.username, user.email, user.password)
    bg.add_task(emailer.send_verification_mail, user.email, user.username, vid)
    return user_profile


@userRouter.get("/{user_id}", description="get user by id")
async def get_user_by_id(user_id: str):
    return (await mayor.get_by_id(user_id))
