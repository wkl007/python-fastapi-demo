from fastapi import FastAPI
from pydantic import BaseModel
from enum import Enum

app = FastAPI()


class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None


class ModelName(str, Enum):
    alexnet = 'alexnet'
    resnet = 'resnet'
    lenet = 'lenet'


fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get('/')
async def root():
    return {'message': 'Hello World'}


# 查询参数，默认值
@app.get('/items/')
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip:skip + limit]


# 可选参数
@app.get('/items/{item_id}')
def read_item(item_id: int, q: str | None = None, short: bool = False):
    item = {'item_id': item_id}
    if q:
        item.update({'q': q})
    if not short:
        item.update({'description': 'This is an amazing item that has a long description'})
    return item


@app.put('/items/{item_id}')
def update_item(item_id: int, item: Item):
    return {'item_name': item.name, 'item_id': item_id, "item_price": item.price}


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
