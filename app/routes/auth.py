from fastapi import APIRouter, Request, Response
from utils.rabbit import sessioner
from schemas.auth import LoginDataEmail, LoginDataUsername
import pytz
import datetime

authRouter = APIRouter(prefix="/auth", tags=["auth"])


@authRouter.post("/", description="login user")
async def create_user(
    data: LoginDataEmail | LoginDataUsername, req: Request, resp: Response
):
    sid = await sessioner.create(
        dict(data).get("email") or dict(data).get("password"),
        data.password,
        ip=req.client.host,
    )
    resp.set_cookie(
        "session",
        value=sid,
        expires=int(datetime.timedelta(days=2).total_seconds()),
        httponly=True,
    )
    return {"ok": 1}


@authRouter.get("/verify")
async def verify_user(token: str):
    d = await r.call("auth.verify", {"token": token})
    if d["ok"] == 1:
        return {"verified": True}
    else:
        return {"verified": False}
