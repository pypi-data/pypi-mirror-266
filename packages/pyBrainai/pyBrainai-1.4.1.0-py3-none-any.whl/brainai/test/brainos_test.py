import time
from urllib.parse import urlparse, parse_qs

import brainai
import json

# help_api_key = "Ub8cWZ9JzKMzfXOl5783167765Ed4376B1BbA06d0fF10755"
# help_api_base = "http://10.0.36.13:8888/brain"
help_api_key = "iFt20LWHsmzSLsM71638Ef67A3694eF893EeD834228aE459"
help_api_base = "https://brain.thundersoft.com/brain"

app_id = "1777633445126377472"
user_id = "test-13011033796"

common_parameters = {
    "api_key": help_api_key,
    "api_base": help_api_base,
    "headers": {
        "appId": app_id,
        "userId": user_id,
    }
}


def read_files():
    file_paths = ["D:\\file\\研发经理任职资格体系介绍.docx", ]  # 要上传的文件路径列表
    # 构建 multipart/form-data 请求体
    files = []
    for file_path in file_paths:
        # 获取文件的 MIME 类型
        # mime_type = "application/octet-stream"
        # 打开文件并读取内容
        with open(file_path, "rb") as file:
            file_data = file.read()
        # 构建文件对象
        files.append(("files", (file_path, file_data)))
    return files


# 创建知识库
def create_knowledge():
    kwargs = {
        "object_name": "knowledge.api.knowledge.pub_create",
        "knowledge_name": "团队空间_测试权限110",
        "description": "这个团队空间只为测试而用......",
        "visible_state": 2,
        "space_users": {
            "287": "0",
        },
    }
    kwargs.update(common_parameters)
    json_str = json.dumps(kwargs, indent=4, ensure_ascii=False)
    print(f"json={json_str}")
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return
    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 获取空间列表
def knowledge_list():
    kwargs = {
        "object_name": "knowledge.api.knowledge.pub_knowledge_list?app_type=0",
        "filter_type": 4,  # PERSON = 1  #个人  TEAM = 2  #团队  COMPANY = 3  #企业  ALL = 4  #全部
        "keyword": "",
        "search_type": 1,  # 1 个人（我的）空间  2 团队空间  3 企业空间
        "page": 1,
        "size": 20,
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return
    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 删除空间
def delete_knowledge():
    knowledge_id = 1767821415425376258
    kwargs = {
        "object_name": f"knowledge.api.knowledge.pub_delete_knowledge.{knowledge_id}",
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 上传文件
def upload_files():
    kwargs = {
        "api_key": help_api_key,
        "api_base": help_api_base,
        "object_name": "dandelion.api.v1.file",
        "files": read_files(),
    }
    response = brainai.BrainOsCompletion.uploadFiles(**kwargs)
    data = json.loads(response.text)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 文件学习
def files_learn():
    kwargs = {
        "object_name": "knowledge.api.file.pub_learning",
        "group_id": "0",
        "knowledge_id": "1764985334501867521",
        "type": 0,
        "files": [
            {
                "size": "3228148",
                "name": "研发经理任职资格体系介绍.docx",
                "originUrl": "http://127.0.0.1:9000/dandelion/test/20240305/24d88d2157286e6f8b42df5e43dbf9d3.docx",
                "customFileType": "NORMAL"
            }
        ]
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 获取文件列表
def file_list():
    kwargs = {
        "object_name": f"dandelion.api.v1.dataset.files.listByUserId?userId={user_id}",
        "method": "GET",
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 删除文件列表
def delete_file_list():
    knowledge_id = 1764985334501867521
    kwargs = {
        "object_name": f"knowledge.api.knowledge.pub_delete_files?knowledge_id={knowledge_id}&action=delete",
        "file_ids": ["1764987438054375426", "1764987438054375427"]
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 添加对话(助手聊天)
def add_chat():
    kwargs = {
        "object_name": "brain.api-public.v1.chat",
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 获取对话历史
def history_chat():
    chat_id = 1765199189163061248
    kwargs = {
        "object_name": f"brain.api-public.v1.history.{chat_id}?pageSize=20&pageNum=0&id=0",
        "method": "GET",
    }
    kwargs.update(common_parameters)
    if "object_name" in kwargs:
        object_name = kwargs.pop("object_name")
        # 解析URL字符串成URL对象
        url_obj = urlparse(object_name)
        # 将查询参数解析为字典对象
        query_params = parse_qs(url_obj.query)
        pageSize = query_params.get("pageSize", None)
        pageNum = query_params.get("pageNum", None)
        id = query_params.get("id", None)
        if not pageSize or not pageNum or not id:
            res = {
                "code": -1,
                "data": "",
                "message": "'PageSize', 'pageNum', and 'id' must all be present !"
            }
            return json.dumps(res)

        try:
            n = int(pageSize[0])
            if n == 0:
                res = {
                    "code": -1,
                    "data": "",
                    "message": "'PageSize' parameter error!"
                }
                return json.dumps(res)
        except ValueError:
            res = {
                "code": -1,
                "data": "",
                "message": "'PageSize' parameter error!"
            }
            return json.dumps(res)

        try:
            n = int(pageNum[0])
        except ValueError:
            res = {
                "code": -1,
                "data": "",
                "message": "'pageNum' parameter error!"
            }
            return json.dumps(res)
        try:
            n = int(id[0])
        except ValueError:
            res = {
                "code": -1,
                "data": "",
                "message": "'id' parameter error!"
            }
            return json.dumps(res)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# brain下基于模型的对话
def llm_chat():
    stream = True
    kwargs = {
        "object_name": "brain.api-public.v1.completions",
        "chatId": "",
        "reGenerate": 0,
        "messagesId": 321324354675,
        "message": "中国最好的画家是谁?",
        "ignoreHistory": 0,  # 1是不保存,0是保存
        "stream": stream
    }
    kwargs.update(common_parameters)
    response = brainai.ChatCompletion.create(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    if not stream:
        print(f"response type={response}")
        data = json.loads(response)
        print(f"{json.dumps(data, indent=4, ensure_ascii=False)}")
    else:
        for chunk in response:
            data = json.loads(chunk)
            print(f"{json.dumps(data, indent=4, ensure_ascii=False)}")


# brain下带知识库的对话
def knowledge_chat():
    chat_id = 1765199189163061248
    knowledge_id = 1764985334501867521
    stream = True
    kwargs = {
        "object_name": "brain.api-public.v1.qa.completions",
        "knowledges": [
            {
                "id": knowledge_id,
                "name": ""
            }
        ],
        "appId": app_id,
        "chatId": chat_id,
        "reGenerate": 0,
        "messagesId": 0,
        "message": "项目经理的职责是什么？",
        "ignoreHistory": 0,
        "stream": stream
    }
    kwargs.update(common_parameters)
    response = brainai.ChatCompletion.create(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    if not stream:
        print("----" + response)
        # data = json.loads(response)
        # print(f"{json.dumps(data,indent=4 ,ensure_ascii=False)}")
    else:
        for chunk in response:
            data = json.loads(chunk)
            print(f"{json.dumps(data, indent=4, ensure_ascii=False)}")


# 删除对话
def delete_chat():
    chat_id = 1765199189163061248
    kwargs = {
        "object_name": f"brain.api-public.v1.chat.{chat_id}",
        "method": "DELETE",
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return

    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


# 获取对话列表
def chat_list():
    kwargs = {
        "object_name": f"brain.api-public.v1.chat.list",
        "method": "GET",
    }
    kwargs.update(common_parameters)
    response = brainai.BrainOsCompletion.dealRequest(**kwargs)
    if type(response) == brainai.error.APIError:
        print(f"{response.http_status},{response.http_body}")
        return
    data = json.loads(response)
    json_data = json.dumps(data, indent=4, ensure_ascii=False)
    print(json_data)


if __name__ == '__main__':
    # 创建知识库
    create_knowledge()
    # # 获取空间列表
    # knowledge_list()
    # # 删除空间
    # delete_knowledge()
    # # 上传文件
    # upload_files()
    # # 文件学习
    # files_learn()
    # # 获取文件列表
    # file_list()
    # # 删除文件列表
    # delete_file_list()
    # # 添加对话(助手聊天)
    # add_chat()
    # # 获取对话历史
    # history_chat()
    # # brain下基于模型的对话
    # llm_chat()
    # # brain下带知识库的对话
    # knowledge_chat()
    # # 删除对话
    # delete_chat()
    # # 获取对话列表
    # #chat_list()
