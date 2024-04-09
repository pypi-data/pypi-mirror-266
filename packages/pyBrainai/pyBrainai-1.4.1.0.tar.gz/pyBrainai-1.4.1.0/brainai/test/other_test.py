import threading
from urllib.parse import urlsplit,urlunsplit

url = 'https://example.com/path/to/resource?key1=value1&key2=value2'

_thread_context = threading.local()  #虽是全局对象，但子线程使用此对象，又是各自私有的

_thread_context.xxx = "abc" #在主线程定义的变量xxx ，其它子线程是访问不到的


if __name__ == '__main__':
    #1、
    parsed_url = urlsplit(url)

    print(f"scheme={parsed_url.scheme}")
    print(f"netloc={parsed_url.netloc}")
    print(f"path={parsed_url.path}")
    print(f"query={parsed_url.query}")
    print(f"fragment={parsed_url.fragment}")

    url = urlunsplit((parsed_url.scheme, parsed_url.netloc, parsed_url.path, parsed_url.query, parsed_url.fragment))
    print(f"url ={url}")
    #2、

    ''''
    Callable 是 Python 的一个类型提示，属于 typing 模块中的一部分。它用于表示对象是否可被调用（即函数、方法、类等）。
    Callable 可以用于在类型提示中指定一个可调用对象的类型。
    以下是一个示例，展示如何在类型提示中使用 Callable：
    '''

    from typing import Callable, Optional, Union


    def apply_operation(operation: Callable[[int, int], int], a: int, b: int) -> int:
        return operation(a, b)

    def add(x: int, y: int) -> int:
        return x + y

    result = apply_operation(add, 5, 3)
    print(result)  # Output: 8
    '''
    在上面的例子中，我们定义了一个函数  apply_operation，它接受一个可调用对象 operation、两个整数类型的参数 a 和 b，并返回一个整数类型的结果。
    使用  Callable 类型提示可以清楚地表明 operation 参数应该是一个可调用对象，接受两个整数类型的参数，并返回一个整数类型的值。
    在函数体内部，我们调用 operation(a, b) 来执行指定的操作。
    然后，我们定义了一个名为  add 的函数，它接受两个整数参数并返回它们的和。
    最后，我们调用 apply_operation，将  add 函数作为可调用对象传递，并提供两个整数作为参数。打印结果为 8，即将 5 和  3 相加的结果。
    请注意，Callable 并不是一个具体的类型，而是一个类型提示。它用于指示对象是否可被调用，以及可调用对象的参数类型和返回值类型。
    '''
    #3、
    import requests
    def get_session() -> requests.Session:
        return requests.Session()

    def perform_request(url: str, session: Optional[
        Union["requests.Session", Callable[[], "requests.Session"]]] = None) -> requests.Response:
        if session is None:
            session = requests.Session()  # Create a new session if not provided
        elif callable(session):
            session = session()  # Call the factory function to get a session object

        response = session.get(url)
        return response


    # Example usage
    response1 = perform_request("https://example.com")  # Use a new session
    response2 = perform_request("https://example.com", requests.Session)  # Use the provided session object
    response3 = perform_request("https://example.com", get_session())  # Use the session created by the factory function

    # 4、
    '''
    在Python中， ** params
    是一种特殊的语法，用于在函数调用时传递关键字参数。它允许将一个字典中的键值对作为关键字参数传递给函数。
    以下是 ** params
    的基本用法示例：
    '''
    def greet(name, age):
        print(f"Hello {name}, you are {age} years old.")


    person = {"name": "Alice", "age": 25}
    greet(**person)
    '''
    在这个例子中，我们定义了一个函数 greet，它接受两个参数 name 和 age。
    然后，我们创建了一个字典 person，其中包含了函数所需的关键字参数。
    通过在函数调用时使用 **person，我们将字典中的键值对作为关键字参数传递函数。
    需要注意的是，字典中的键必与函数定义中的参数名相匹配，否则会引发 TypeError。
    '''

