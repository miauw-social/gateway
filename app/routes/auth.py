from fastapi import APIRouter, Request, Response
from rabbit.rabbit import r
from schemas.auth import LoginDataEmail, LoginDataUsername
import pytz
import datetime

authRouter = APIRouter(prefix="/auth", tags=["auth"])

@authRouter.post("/", description="login user")
async def create_user(data: LoginDataEmail| LoginDataUsername, req: Request, resp: Response):
    user_profile = await r.call("user.find", {"login": data.email if type(data) is LoginDataEmail else data.username})
    session = await r.call("auth.login", {"password": data.password, "id": str(user_profile["id"]), "ip": req.client.host})
    resp.set_cookie("session", value=session["id"], expires=int(datetime.timedelta(days=2).total_seconds()), httponly=True)
    return {"ok": 1}


@authRouter.get("/verify")
async def verify_user(token: str):
    d = await r.call("auth.verify", {"token": token})
    if d["ok"] == 1:
        return {"verified": True}
    else:
        return {"verified": False}
