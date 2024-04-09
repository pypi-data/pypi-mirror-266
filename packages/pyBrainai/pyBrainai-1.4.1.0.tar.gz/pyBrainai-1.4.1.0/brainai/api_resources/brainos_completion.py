import json
import time

from brainai import util
from brainai.api_resources.abstract.engine_api_resource import EngineAPIResource
from brainai.error import TryAgain
from urllib.parse import urlparse, parse_qs

class BrainOsCompletion(EngineAPIResource):
    engine_required = False
    OBJECT_NAME = ""

    @classmethod
    def create(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.

        See https://platform.brainai.com/docs/api-reference/chat/create
        for a list of valid parameters.
        """
        start = time.time()
        timeout = kwargs.pop("timeout", None)

        if "object_name" in kwargs:
            cls.OBJECT_NAME = kwargs.pop("object_name")
        if "model" not in kwargs:
            new_kwargs = {"model": "rubik6-chat"}  # 新的参数
            kwargs.update(new_kwargs)

        while True:
            try:
                return super().create(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)

    @classmethod
    async def acreate(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.

        See https://platform.brainai.com/docs/api-reference/chat/create
        for a list of valid parameters.
        """
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        if "object_name" in kwargs:
            cls.OBJECT_NAME = kwargs.pop("object_name")
        if "model" not in kwargs:
            new_kwargs = {"model": "rubik6-chat"}  # 新的参数
            kwargs.update(new_kwargs)

        while True:
            try:
                return await super().acreate(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)
    @classmethod
    def dealRequest(cls, *args, **kwargs):
        """
        Creates a new chat completion for the provided messages and parameters.

        See https://platform.brainai.com/docs/api-reference/chat/create
        for a list of valid parameters.
        """
        start = time.time()
        timeout = kwargs.pop("timeout", None)
        if "object_name" in kwargs:
            cls.OBJECT_NAME = kwargs.pop("object_name")
        if "headers" in kwargs:
            headers = kwargs.get("headers")
            if "userId" in headers:
                userId = headers.get("userId")
                if userId and len(userId) > 64:
                    res = {
                        "code": -1,
                        "data": "",
                        "message": "The length of userId is less than 64 characters!"
                    }
                    return json.dumps(res)

        if "model" not in kwargs:
            new_kwargs = {"model": "rubik6-chat"}  # 新的参数
            kwargs.update(new_kwargs)
        while True:
            try:
                return super().create(*args, **kwargs)
            except TryAgain as e:
                if timeout is not None and time.time() > start + timeout:
                    raise

                util.log_info("Waiting for model to warm up", error=e)

    @classmethod
    def uploadFiles(cls, **kwargs):
        import requests
        url = kwargs.get("api_base") + "/" + kwargs.get("object_name").replace(".", "/")
        print(url)
        # for f in kwargs.get("files"):
        #     print(f)
        response = requests.post(url, files=kwargs.get("files"))
        return response

    @classmethod
    def dealRequestV2(cls, **kwargs):
        import requests
        url = kwargs.get("api_base") + "/" + kwargs.get("object_name").replace(".", "/")
        hd = kwargs.get("headers", None)
        if hd is not None:
            response = requests.post(url, headers=hd)
            return response
