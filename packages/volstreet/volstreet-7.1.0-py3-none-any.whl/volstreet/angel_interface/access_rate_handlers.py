import asyncio
import functools
from datetime import datetime
from time import sleep
import threading
from collections import defaultdict
from volstreet.config import logger
from volstreet.utils.core import current_time


class SemaphoreFactory:
    semaphores = defaultdict(dict)

    @classmethod
    def get_semaphore(cls, identifier, max_limit):
        loop = asyncio.get_running_loop()
        if identifier not in cls.semaphores[loop]:
            cls.semaphores[loop][identifier] = asyncio.Semaphore(max_limit)
        return cls.semaphores[loop][identifier]


class LockFactory:
    locks = defaultdict(dict)

    @classmethod
    def get_lock(cls, identifier):
        loop = asyncio.get_running_loop()
        if identifier not in cls.locks[loop]:
            cls.locks[loop][identifier] = asyncio.Lock()
        return cls.locks[loop][identifier]


# A class based implementation for educating myself on decorators
class AccessRateHandler:
    def __init__(self, delay=1):
        self.delay = delay + 0.1  # Add a small buffer to the delay
        self.last_call_time = datetime(
            1997, 12, 30
        )  # A date with an interesting trivia in the field of CS

    def __call__(self, func):
        def wrapped(*args, **kwargs):
            time_since_last_call = (
                current_time() - self.last_call_time
            ).total_seconds()
            if time_since_last_call < self.delay:
                sleep(self.delay - time_since_last_call)
            result = func(*args, **kwargs)
            self.last_call_time = current_time()
            return result

        return wrapped


def access_rate_handler(*, max_requests=None, per_seconds=None, is_async=False):
    request_times: list[datetime] = []

    if not is_async:
        sem = threading.Semaphore(max_requests)
        lock = threading.Lock()

        def remove_expired_request_times():
            nonlocal request_times, lock
            with lock:
                time_now = current_time()
                request_times = [
                    t
                    for t in request_times
                    if (time_now - t).total_seconds() < per_seconds
                ]

    def decorator(func):
        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            nonlocal request_times
            with sem:
                remove_expired_request_times()
                while len(request_times) >= max_requests:
                    remove_expired_request_times()
                    sleep(0.01)
                request_times.append(current_time())

            result = func(*args, **kwargs)
            return result

        @functools.wraps(func)
        async def async_wrapped(*args, **kwargs):
            nonlocal request_times
            semaphore = SemaphoreFactory.get_semaphore(func.__name__, max_requests)
            async_lock = LockFactory.get_lock(func.__name__)

            async with semaphore:
                async with async_lock:
                    length_of_request_times = len(request_times)
                while length_of_request_times >= max_requests:
                    async with async_lock:
                        time_now = current_time()
                        request_times = [
                            t
                            for t in request_times
                            if (time_now - t).total_seconds() < per_seconds
                        ]
                    await asyncio.sleep(0.01)
                    async with async_lock:
                        length_of_request_times = len(request_times)
                async with async_lock:
                    request_times.append(current_time())

            result = await func(*args, **kwargs)
            return result

        return async_wrapped if is_async else wrapped

    return decorator


async def rate_handler_generator(
    coros: list,
    requests_per_sec: int,
):
    """A generator that yield results as and when they become available. Handles rate limiting."""
    pending = set()
    start_times = []

    while coros or pending:
        time_now = datetime.now()
        start_times = [t for t in start_times if (time_now - t).total_seconds() < 1.1]

        while len(start_times) < requests_per_sec:
            try:
                task = coros.pop(0)
            except IndexError:
                break
            start_times.append(datetime.now())
            pending.add(asyncio.ensure_future(task))

        if not pending:
            if coros:
                oldest_time = min(start_times)
                sleep_time = max(0, 1.1 - (time_now - oldest_time).total_seconds())
                await asyncio.sleep(sleep_time)
                continue
            else:
                return

        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        while done:
            yield done.pop().result()


async def rate_handler_generator_with_retries(
    tasks: list,
    requests_per_sec: int,
):
    """A generator that yield results as and when they become available. Handles rate limiting."""
    pending = set()
    start_times = []
    retry_queue = []
    attempt_map = {task: 0 for task in tasks}

    while tasks or pending or retry_queue:
        time_now = datetime.now()
        start_times = [t for t in start_times if (time_now - t).total_seconds() < 1.1]

        while (len(start_times) < requests_per_sec) and (tasks or retry_queue):
            if retry_queue:
                task = retry_queue.pop(0)
            elif tasks:
                task = tasks.pop(0)
            else:
                break
            start_times.append(datetime.now())
            pending.add(asyncio.ensure_future(task))

        if not pending:
            if tasks:
                oldest_time = min(start_times)
                sleep_time = max(0, 1.1 - (time_now - oldest_time).total_seconds())
                await asyncio.sleep(sleep_time)
                continue
            else:
                return

        done, pending = await asyncio.wait(pending, return_when=asyncio.FIRST_COMPLETED)

        while done:
            # Reattempt failed tasks
            result = done.pop()
            if result.exception():
                logger.error(
                    f"Task failed with exception: {result.exception()}. Attempt: {attempt_map[result._coro]}"
                )
                if attempt_map[result._coro] < 3:
                    retry_queue.append(result._coro)
                    attempt_map[result._coro] += 1
                else:
                    yield {"error": result.exception()}
            else:
                yield result.result()
