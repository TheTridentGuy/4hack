import fastapi
from fastapi import FastAPI, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn


from config import HOST, PORT, DEBUG


app = FastAPI()
templates = Jinja2Templates(directory="/templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: fastapi.Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/client", response_class=HTMLResponse)
async def client(request: fastapi.Request):
    return templates.TemplateResponse("client.html", {"request": request})


if __name__ == "__main__":
    uvicorn.run("app:app", host=HOST, port=PORT, reload=DEBUG)
