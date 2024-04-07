import asyncio
import random

async def producer(queue, n):
    for i in range(n):
        item = random.randint(1, 100)
        await queue.put(item)
        print(f"Producer produced item: {item}")
        await asyncio.sleep(random.random() * 2)

    await queue.put(None)  # 发送一个特殊的值表示生产结束

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break

        print(f"Consumer consumed item: {item}")
        await asyncio.sleep(random.random())

async def main():
    queue = asyncio.Queue()
    producer_task = asyncio.create_task(producer(queue, 10))
    consumer_task = asyncio.create_task(consumer(queue))
    await asyncio.gather(producer_task, consumer_task)

asyncio.run(main())
