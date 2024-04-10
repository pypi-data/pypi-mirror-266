"""
This plugin is used to track pop enabled background task capabilities
"""

from collections.abc import Callable
from collections.abc import Coroutine


async def auto(hub, coro: Coroutine, cb_coro=None):
    """
    Start a task that will be automatically awaited

    coro: An unscheduled coroutine object to run
    cb_coro: An unscheduled coroutine to run when the main coroutine completes
    """
    task = hub._auto(coro, cb_coro)
    await hub.lib.asyncio.sleep(0)
    return task


async def wait(hub):
    """
    When running without a long-running loop, (hub.aio.loop.run instead of hub.aio.loop.start)
    you need to call this function to clean up any auto tasks that have been created in the
    background.
    This function can be called from anywhere, it will just wait for all auto tasks to
    complete
    """
    while not hub._tasks.empty():
        complete = await hub._tasks.get()
        await complete["task"]
        if complete["cb"]:
            await hub.pop.task.auto(complete["cb"])


async def keep_alive(hub, precision: int, func: Callable, **kwargs):
    """
    Make sure that the named function stays alive, if the resulting coroutine dies, restart the function.
    The operation is run in a separate auto task

    :param precision: The number in seconds to sleep between checks
    :param func: The async function reference to restart if it dies
    :param **kwargs: The keyword arguments to send to the function to start and keep alive
    """

    async def _keep_alive():
        f_id = hub.lib.uuid.uuid4().hex
        if f_id not in hub._aio_alive:
            hub._aio_alive[f_id] = {"task": None}
        while True:
            start = False
            if hub._aio_alive[f_id]["task"] is None:
                start = True
            elif hub._aio_alive[f_id]["task"].done():
                await hub._aio_alive[f_id]["task"]
                start = True
            if start:
                hub._aio_alive[f_id]["task"] = await hub.pop.task.auto(func(**kwargs))
            await hub.lib.asyncio.sleep(precision)

    await hub.pop.task.auto(_keep_alive())
