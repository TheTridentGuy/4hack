from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from prisma import Prisma
import uvicorn
import fastapi


from config import HOST, PORT, DEBUG, DEFAULT_ADMIN_USERNAME, DEFAULT_ADMIN_PASS_HASH


# Lifespan events for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup()
    yield
    await shutdown()

async def startup():
    await db.connect()
    admins = await db.user.find_many(where={"role": "ADMIN"})
    if not admins:
        await db.user.create(data={
        "username": DEFAULT_ADMIN_USERNAME,
        "pass_hash": DEFAULT_ADMIN_PASS_HASH,
        "role": "ADMIN",
        "display_name": "Admin",
        "bio": "Default admin user"
    })

async def shutdown():
    await db.disconnect()

# Setup FastAPI app, Jinja2 templates, static files, and Prisma client
app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
db = Prisma()

# App routes
@app.get("/", response_class=HTMLResponse)
async def index(request: fastapi.Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/client", response_class=HTMLResponse)
async def client(request: fastapi.Request):
    return templates.TemplateResponse("client.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login(request: fastapi.Request):
    return templates.TemplateResponse("login.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=DEBUG)
