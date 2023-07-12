from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from rabbit.rabbit import r, LOOP
from routes.user import userRouter
from uvicorn import Config, Server

app = FastAPI(title="Gateway -  miauw")
app.include_router(userRouter)


@app.get("/")
async def main(time: int = 0):
    await asyncio.sleep(10)
    return "ok"


@app.get("/health")
async def health():
    return {"ok": 1}


@app.on_event("startup")
async def setup():
    await r.connect()
    
    

@app.on_event("shutdown")
async def end():
    pass

if __name__ == "__main__":
    config = Config(app=app, loop=LOOP)
    server = Server(config)
    LOOP.run_until_complete(server.serve())
