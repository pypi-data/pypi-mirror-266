import asyncio
import os
import time
from sparrow.api import create_app
import uvicorn


async def iterfunc():
    for i in range(10):
        await asyncio.sleep(0.1)
        yield i


async def func1():
    time.sleep(1)
    print("func1")
    # await asyncio.sleep(1)
    for i in range(10):
        await asyncio.sleep(0.1)
        print(f"func1:{i}")

    print("func1 已完成")


async def func2():
    print("func2")
    await asyncio.sleep(0.5)
    for i in range(10):
        await asyncio.sleep(0.1)
        print(f"func2:{i}")
    print("func2 已完成")


async def asynchronous_function():
    def blocking_operation():
        # 模拟耗时的阻塞操作
        # 这里可以是任何耗时的同步操作
        print("aaaa")
        time.sleep(1)
        print("阻塞操作完成")
        return '哈哈哈哈哈'
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, blocking_operation)

async def ttt():
    """如果内部是完全同步的，没有await，则执行该函数时会被串行执行。"""
    print("tttttt")
    time.sleep(4)
    print("111111")
    return 11111


async def main():
    print('action')
    res = await asyncio.gather( ttt(),func1(), func2(), asynchronous_function(),)
    #如果只有一个，则可以用create_task
    # task1 = asyncio.create_task(func1())
    # await task1
    return res
def run():
    res = asyncio.run(main())
    print(res)
    print("allala")


run()
