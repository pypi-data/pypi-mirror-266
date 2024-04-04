# -*- coding: utf-8 -*-

from secrets import randbits
import signal
from sys import exc_info
from threading import Condition
from time import sleep
from typing import Union

from .constants import DEFAULT_SLEEP_TIME, MAX_SLEEP_TIME, Status
from .keep_alive import KeepAliveThread
from .logger import logger
from .queue import Queue
from .task import PyTask

class Worker:
    """Worker is the class of Python task worker.

    Args:
        queue (delayed.queue.Queue): The task queue of the worker.
        keep_alive_interval (int or float): The worker marks itself as alive for every `keep_alive_interval` seconds.
        id_bits (int): The bits used for the worker ID. The default value is 16, which is enough for 2 ** 16 workers.
    """

    def __init__(
        self,
        queue: Queue,
        keep_alive_interval: Union[int, float] = 15,
        id_bits: int = 16
    ):
        self._queue = queue
        self._keep_alive_interval = keep_alive_interval
        self._id_bits = id_bits
        self._status = Status.STOPPED
        self._cond = Condition()

    def generate_id(self):
        """Generates a random ID for the worker."""
        while True:
            self._queue._worker_id = self._id = randbits(self._id_bits)
            if self._queue.try_online():
                return

    def run(self):  # pragma: no cover
        """Runs the worker."""
        self.generate_id()

        logger.debug('Starting worker %d.', self._id)
        self._status = Status.RUNNING
        self._register_signals()

        thread = KeepAliveThread(self)
        thread.start()

        try:
            sleep_time = DEFAULT_SLEEP_TIME
            while self._status == Status.RUNNING:
                try:
                    task = self._queue.dequeue()
                except Exception:  # pragma: no cover
                    logger.exception('Failed to dequeue task.')
                    sleep(sleep_time)
                    sleep_time *= 2
                    if sleep_time > MAX_SLEEP_TIME:
                        sleep_time = MAX_SLEEP_TIME
                else:
                    sleep_time = DEFAULT_SLEEP_TIME
                    if task:
                        try:
                            task.execute()
                        except Exception:
                            logger.exception('Failed to execute task %s.', task._func_path)

                            need_retry = False
                            if task._retry:
                                _, _, exc_traceback = exc_info()
                                if exc_traceback:
                                    tb_next = exc_traceback.tb_next
                                    if tb_next:
                                        tb_next2 = tb_next.tb_next
                                        if tb_next2:
                                            # invalid call, should not be retried
                                            need_retry = True
                                            # delete tracebacks to avoid memory leak
                                            del tb_next2
                                        del tb_next
                                    del exc_traceback

                            if need_retry:
                                self._retry_task(task)
                            else:
                                self._release_task()
                        else:
                            self._release_task()
        finally:
            self._unregister_signals()
            self._status = Status.STOPPED
            with self._cond:
                self._cond.notify()
            thread.join()
            logger.debug('Stopped worker %d.', self._id)

    def stop(self):
        """Stops the worker."""
        if self._status == Status.RUNNING:
            logger.debug('Stopping worker %d.', self._id)
            self._status = Status.STOPPING

    def _retry_task(self, task: PyTask):
        """Retries a dequeued task.

        Args:
            task (delayed.task.PyTask): The task to be retried.
        """
        if task._retry:
            if task._retry > 0:
                task._retry -= 1
            task._data = None
            task.serialize()

            logger.debug('Retrying task %s', task._func_path)
            try:
                self._queue.enqueue(task, release=True)
            except Exception:  # pragma: no cover
                logger.exception('Failed to retry task %s', task._func_path)

    def _release_task(self):
        """Releases the currently dequeued task."""
        try:
            self._queue.release()
        except Exception:  # pragma: no cover
            logger.exception('Failed to release task of worker %d.', self._id)

    def _register_signals(self):
        """Registers signal handlers."""
        def stop(signum, frame):
            logger.debug('Received SIGHUP.')
            self.stop()
        signal.signal(signal.SIGHUP, stop)

    def _unregister_signals(self):
        """Unregisters signal handlers."""
        signal.signal(signal.SIGHUP, signal.SIG_DFL)
