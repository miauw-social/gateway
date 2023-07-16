from fastapi import Request, HTTPException
from utils.rabbit import r

async def protected_route(req: Request):
    logged_in = await r.call("auth.session.exists", {"sid": req.cookies["session"]})
    if not logged_in:
        raise HTTPException(401, "not authorized")


async def current_user():
    pass