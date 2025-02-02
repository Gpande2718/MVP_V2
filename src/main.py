import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from web.api import app as api_app
import os

# Create main FastAPI app
app = FastAPI(title="Assignment Grading System")

# Mount the API router
app.mount("/api", api_app)

# Mount static files
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="src/web/templates")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 