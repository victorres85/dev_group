import os
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

ALLOWED_HOSTS = ["*"]
SECRET_KEY="YEIwR!8YgdkmEWl8f%:T~2dp,i1K46f)@a?e[FzXBOL@pnmZ>J(r}L!MdS0"

# SECRET_KEY = os.environ.get('SECRET_KEY')

def setup_middleware(app: FastAPI):
    app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )