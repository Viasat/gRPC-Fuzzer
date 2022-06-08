import asyncio

async def max_concurrent(num_workers, task_generator):
    async def worker():
        async for task in task_generator:
            await task
    await asyncio.gather(*[worker() for i in range(num_workers)])
