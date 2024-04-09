import asyncio
import time

import brainai
import json


model_api_key = "Ub8cWZ9JzKMzfXOl5783167765Ed4376B1BbA06d0fF1072d"
model_api_base = "http://10.0.36.13:8888/brain"

common_parameters ={
        "api_key": model_api_key,
        "api_base": model_api_base,
}

# 获取模型列表
def model_list():
    kwargs = {
        "object_name": "billing.v1.models.available",
        "method": "GET",
    }
    kwargs.update(common_parameters)
    response = brainai.ChatCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return
    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)

async def await_test(**kwargs):
    start_time = time.time()
    is_first = True
    async for response in await brainai.BrainOsCompletion.acreate(**kwargs):
        if is_first:
            is_first = False
            end_time = time.time()
            print("-----首字耗时 {:.2f}秒".format(end_time - start_time))
        print(response)
async def test(**kwargs):
   await await_test(**kwargs)

# 基于模型聊天
def model_chat():
    stream = True
    kwargs = {
        "object_name": "billing.v1.chat.completions",
        "model": "rubik6-chat",
        "messages": [
            {
                "role": "user",
                "content": "魔方大脑有什么功能？",
            }
        ],
        "temperature": 0,
        "stream": stream
    }
    kwargs.update(common_parameters)
    #方法1：
    response = brainai.ChatCompletion.create(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    for chunk in response:
        print(f"{json.dumps(chunk,ensure_ascii=False)}")
    #方法2：
    #asyncio.run(await_test(**kwargs))
    #方法3:
    #asyncio.run(test(**kwargs))

if __name__ == '__main__':
    # 获取模型列表
    model_list()
    # 基于模型聊天
    model_chat()







