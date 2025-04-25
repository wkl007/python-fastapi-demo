"""
.
├── app                  # 「app」是一个 Python 包
│   ├── __init__.py      # 这个文件使「app」成为一个 Python 包
│   ├── main.py          # 「main」模块，例如 import app.main
│   ├── dependencies.py  # 「dependencies」模块，例如 import app.dependencies
│   └── routers          # 「routers」是一个「Python 子包」
│   │   ├── __init__.py  # 使「routers」成为一个「Python 子包」
│   │   ├── items.py     # 「items」子模块，例如 import app.routers.items
│   │   └── users.py     # 「users」子模块，例如 import app.routers.users
│   └── internal         # 「internal」是一个「Python 子包」
│       ├── __init__.py  # 使「internal」成为一个「Python 子包」
│       └── admin.py     # 「admin」子模块，例如 import app.internal.admin
"""
from fastapi import Depends, FastAPI

from .dependencies import get_query_token, get_token_header
from .internal import admin
from .routers import items, users

app = FastAPI(dependencies=[Depends(get_query_token)])

app.include_router(users.router)
app.include_router(items.router)
app.include_router(
    admin.router,
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(get_token_header)],
    responses={418: {"description": "I'm a teapot"}},
)


@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}
