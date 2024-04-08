import abc
import asyncio
import functools
from typing import Any, Dict, List, Tuple


class BaseAsyncIOTask:
    @classmethod
    async def execute(cls, data: Dict = {}) -> Any:
        """
        Executes the async logic by awaiting the task logic
        This function is mainly used by all async application logic to execute async logic
        """
        task = cls()
        return await task.perform_task(**data)

    @classmethod
    def execute_sync(cls, data: Dict = {}) -> Any:
        """This is used to run the asyncio task if any inside a synchronous code"""
        task = cls()
        # If there is an event loop already running, get it otherwise create a new event loop.
        try:
            loop = asyncio.get_event_loop()
            result = loop.run_until_complete(task.perform_task(**data))
            loop.close()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(task.perform_task(**data))
            loop.close()
        return result

    @abc.abstractmethod
    async def perform_task(self, **data) -> Any:
        """
        This function holds the logic of the async task which will be run on the event loop
        """

        raise NotImplementedError('Implement the logic for {}.'.format(self.__class__.__name__))


class BulkTaskExecutor(BaseAsyncIOTask):
    @classmethod
    def execute_sync(cls, data: Dict = {}) -> Any:
        task = cls()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(task.perform_task(**data))
        loop.close()

        return result

    async def perform_task(self, task_list: List[Tuple] = None) -> List:
        loop = asyncio.get_event_loop()
        results = await asyncio.gather(
            *[
                asyncio.ensure_future(loop.run_in_executor(None, functools.partial(*task[0], **task[1])), loop=loop)
                for task in task_list
            ],
            loop=loop,
            return_exceptions=True,
        )

        # If there is exception in performing any task
        # we pass that exception to the parent function instead of returning the results
        for result in results:
            if isinstance(result, Exception):
                raise result

        return [result for result in results]
