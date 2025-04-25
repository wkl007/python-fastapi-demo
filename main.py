from enum import Enum
from typing import Annotated, Literal

from fastapi import FastAPI, Query, Path
from pydantic import BaseModel, Field

app = FastAPI()


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    is_offer: bool | None = None
    tax: float | None = None


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
def update_item(item_id: int, item: Item, q: str | None = None):
    result = {'item_id': item_id, **item.model_dump()}
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

# if __name__ == '__main__':
#     uvicorn.run(app, host='0.0.0.0', port=9000)
