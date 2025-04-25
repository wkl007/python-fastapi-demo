from datetime import datetime, time, timedelta
from enum import Enum
from typing import Annotated, Literal, Any
from uuid import UUID

from fastapi import FastAPI, Query, Path, Body, Cookie, Header
from pydantic import BaseModel, Field, HttpUrl, EmailStr

app = FastAPI()


class Image(BaseModel):
    url: HttpUrl
    name: str


class Item(BaseModel):
    name: str = Field(examples=['Foo'])
    description: str | None = Field(default=None, title='The description of the item', max_length=300)
    price: float = Field(gt=0, description='The price must be greater than zero')
    is_offer: bool | None = None
    tax: float | None = Field(default=None, examples=[3.2])
    tags: set[str] = set()  # set 去重
    image: Image | None = None
    images: list[Image] | None = None

    # model_config = {
    #     'json_schema_extra': {
    #         'examples': [
    #             {
    #                 'name': 'Foo',
    #                 'description': 'A very nice Item',
    #                 'price': 35.4,
    #                 'tax': 3.2
    #             }
    #         ]
    #     }
    # }


class Offer(BaseModel):
    name: str
    description: str | None = None
    price: float
    items: list[Item]


class User(BaseModel):
    username: str
    full_name: str | None = None


class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'


class FilterParams(BaseModel):
    model_config = {'extra': 'forbid'}
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal['created_at', 'updated_at'] = 'created_at'
    tags: list[str] = []


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get('/')
async def root():
    return {'message': 'Hello World'}


# 查询参数，默认值
# 参数声明额外的信息和校验
@app.get('/items/')
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query


# 可选参数
# ge >= gt > le <= lt <
@app.get('/items/{item_id}')
def read_item(item_id: Annotated[int, Path(title='The ID of the item to get', gt=0, le=1000)],
              q: str,
              size: Annotated[float, Query(gt=0, lt=10.5)],
              short: bool = False):
    item = {'item_id': item_id}
    if q:
        item.update({'q': q})
    if size:
        item.update({'size': size})
    if not short:
        item.update({'description': 'This is an amazing item that has a long description'})
    return item


@app.post('/items/')
def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({'price_with_tax': price_with_tax})
    return item_dict


@app.put('/items/{item_id}')
def update_item(item_id: Annotated[int, Path(title='The ID of the item to get', ge=0, le=1000)],
                item: Annotated[Item, Body(embed=True)],
                user: User,
                importance: Annotated[int, Body()],
                q: str | None = None):
    result = {'item_id': item_id, 'item': item, 'user': user, 'importance': importance}
    if q:
        result.update({'q': q})
    return result


@app.get('/users/me')
async def read_user_me():
    return {"user_id": 'the current user'}


@app.get('/users/{user_id}')
async def read_user(user_id: str):
    return {'user_id': user_id}


# 多个路径和查询参数
# 必选查询参数
@app.get('/users/{user_id}/items/{item_id}')
async def read_user_item(user_id: int, item_id: str, needy: str, q: str | None = None, short: bool = False):
    item = {'item_id': item_id, 'owner_id': user_id, 'needy': needy}
    if q:
        item.update({'q': q})
    if not short:
        item.update({'description': 'This is an amazing item that has a long description'})
    return item


# 枚举类
@app.get('/models/{model_name}')
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {'model_name': model_name, 'message': 'Deep Learning FTW!'}

    if model_name.value == 'lenet':
        return {'model_name': model_name, 'message': 'LeCNN all the images!'}

    return {'model_name': model_name, 'message': 'Have some residuals'}


# 路径参数
@app.get('/files/{file_path:path}')
async def read_file(file_path: str):
    return {'file_path': file_path}


@app.post('/offers/')
async def create_offer(offer: Offer):
    return offer


@app.post('/images/multiple/')
async def create_multiple_images(images: list[Image]):
    for image in images:
        print(image.name, image.url)
    return images


@app.post('/index-weights/')
async def create_index_weights(weights: dict[int, float]):
    return weights


@app.put('/items2/{item_id}')
async def read_items2(
        item_id: UUID,
        start_datetime: Annotated[datetime, Body()],
        end_datetime: Annotated[datetime, Body()],
        process_after: Annotated[timedelta, Body()],
        repeat_at: Annotated[time | None, Body()] = None
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }


class Cookies(BaseModel):
    # model_config = {'extra': 'forbid'}
    session_id: str
    fatebook_tracker: str | None = None
    googall_tracker: str | None = None


@app.get('/cookie/')
async def read_cookie(cookies: Annotated[Cookies, Cookie()]):
    return cookies


class CommonHeaders(BaseModel):
    # model_config = {"extra": "forbid"}
    host: str
    save_data: bool
    if_modified_since: str | None = None
    traceparent: str | None = None
    x_tag: list[str] = []


@app.get('/header/')
async def read_header(headers: Annotated[CommonHeaders, Header()]):
    return headers


# response_model_include 包含哪一项，只对当个对象生效，列表对象无用
@app.post('/items3/', response_model=Item, response_model_include={'name'})
async def create_item3(item: Item) -> Any:
    return item


# response_model_exclude_unset 忽略默认值
@app.get('/items3/', response_model=list[Item], response_model_exclude_unset=True)
async def read_item3() -> Any:
    return [
        {
            'name': '小王',
            'price': 1
        },
        {
            'name': '小红',
            'price': 2
        }
    ]


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


@app.post('/user/', response_model=UserOut)
async def create_user(user: UserIn) -> Any:
    return user

# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=9000)
