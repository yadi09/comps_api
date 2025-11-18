# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from app.api import router as api_router

app = FastAPI(title="PropStream Comps")

app.include_router(api_router, prefix="")

templates = Jinja2Templates(directory="app/templates")
# app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# if __name__ == "__main__":
import uvicorn
uvicorn.run(app, host="0.0.0.0", port=8001)