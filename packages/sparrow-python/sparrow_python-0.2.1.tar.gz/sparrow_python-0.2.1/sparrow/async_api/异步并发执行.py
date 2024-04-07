import asyncio

async def async_function1():
    await asyncio.sleep(3)
    return 'Result from async_function1'

async def async_function2():
    await asyncio.sleep(2)
    return 'Result from async_function2'

async def async_function3():
    await asyncio.sleep(1)
    return 'Result from async_function3'

async def main():
    # 创建任务列表
    tasks = [async_function1(),async_function3(), async_function2(), ]
    tasks = [asyncio.create_task(i) for i in tasks]

    # 并发执行任务
    completed, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    print(f"{completed=}")
    # 获取先执行完的任务结果
    print("------------kj")
    for task in completed:
        print(task)
        result = await task
        print(f'Result: {result}')
    print("==============")

# 使用asyncio事件循环运行主函数
asyncio.run(main())
