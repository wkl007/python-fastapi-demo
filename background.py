from fastapi import BackgroundTasks, FastAPI, Depends
from typing import Annotated

description = """
ChimichangApp API helps you do awesome stuff. 🚀

## Items

You can **read items**.

## Users

You will be able to:

* **Create users** (_not implemented_).
* **Read users** (_not implemented_).
"""

tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://fastapi.tiangolo.com/",
        },
    },
]

# app = FastAPI(title='小王测试',
#               description=description,
#               summary="Deadpool's favorite app. Nuff said.",
#               version="0.0.1",
#               terms_of_service="http://example.com/terms/",
#               contact={
#                   "name": "Deadpoolio the Amazing",
#                   "url": "http://x-force.example.com/contact/",
#                   "email": "dp@x-force.example.com",
#               },
#               license_info={
#                   "name": "Apache 2.0",
#                   "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
#               },
#               )
# app = FastAPI(openapi_tags=tags_metadata)
app = FastAPI(docs_url='/test', redoc_url=None)


def write_log(message: str):
    with open("log.txt", mode="a") as log:
        log.write(message)


def get_query(background_tasks: BackgroundTasks, q: str | None = None):
    if q:
        message = f"found query: {q}\n"
        background_tasks.add_task(write_log, message)
    return q


@app.get("/users/", tags=["users"])
async def get_users():
    return [{"name": "Harry"}, {"name": "Ron"}]


@app.get("/items/", tags=["items"])
async def get_items():
    return [{"name": "wand"}, {"name": "flying broom"}]


@app.post("/send-notification/{email}")
async def send_notification(email: str, background_tasks: BackgroundTasks, q: Annotated[str, Depends(get_query)]):
    message = f"message to {email}\n"

    background_tasks.add_task(write_log, message)
    return {"message": "Message sent"}
