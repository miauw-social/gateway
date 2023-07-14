from fastapi import APIRouter, BackgroundTasks
from argon2 import hash_password
from schemas.users import User, UserCreate
from rabbit.rabbit import r


userRouter = APIRouter(prefix="/users", tags=["users"])


async def send_verification_mail(email: str, username: str, vid: str):
    await r.basic_publish_dict(
        "email",
        {
            "type": "sign_up",
            "recipient": email,
            "subject": "Verify your account!",
            "payload": {"link": "http://localhost:8000/auth/verify?token=" + vid, "username": username},
        },
    )

@userRouter.post("/", description="create user")
async def login(user_data: UserCreate, bg:BackgroundTasks):
    
    user_profile: dict = await r.call(
        "user.create", {"email": user_data.email, "username": user_data.username}
    )
    if user_profile.get("error"):
        return
    user = await r.call(
        "auth.password.initial",
        {"password": user_data.password, "id": user_profile["id"]},
    )
    print(user_data.email,user_data.username, user["vid"])
    bg.add_task(send_verification_mail, user_data.email,user_data.username, user["vid"])
    return user_profile


@userRouter.get("/{user_id}", description="get user by id")
async def get_user_by_id(user_id: str):
    print(user)
