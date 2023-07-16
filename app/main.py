from fastapi import FastAPI, Depends, Request
from utils.rabbit import r, LOOP
from utils.exceptions import UserNotFoundException, UserAlreadyExsistsException, ProblemJSONResponse
from routes.user import userRouter
from routes.auth import authRouter
from utils.guards import protected_route
from uvicorn import Config, Server
import time

app = FastAPI(title="Gateway -  miauw")
app.include_router(userRouter)
app.include_router(authRouter)


@app.middleware("http")
async def add_process_time(req, call_next):
    start = time.time()
    resp = await call_next(req)
    end = time.time() - start
    resp.headers["X-Process-Time"] = str(end * 1000)
    return resp

@app.get("/")
async def main(time: int = 0):
    return "ok"


@app.get("/test/", dependencies=[Depends(protected_route)])
async def protected():
    return "Test"

@app.get("/health")
async def health():
    return {"ok": 1}


@app.exception_handler(UserNotFoundException)
async def user_not_found_exception(req: Request, exc: UserNotFoundException):
    return ProblemJSONResponse({**exc.content}, status_code=exc.status_code)

@app.exception_handler(UserAlreadyExsistsException)
async def user_already_exists_exception(req: Request, exc: UserAlreadyExsistsException):
    return ProblemJSONResponse({**exc.content}, status_code=exc.status_code)

@app.on_event("startup")
async def setup():
    await r.connect()
    

@app.on_event("shutdown")
async def end():
    await r.close()

if __name__ == "__main__":
    config = Config(app=app, loop=LOOP)
    server = Server(config)
    LOOP.run_until_complete(server.serve())
