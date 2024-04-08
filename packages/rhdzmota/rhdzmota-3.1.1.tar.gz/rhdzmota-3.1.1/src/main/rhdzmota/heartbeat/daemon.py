from threading import Thread
from typing import Any, Callable, Optional, Union, TYPE_CHECKING

from .daemon_heart import DaemonHeart


if TYPE_CHECKING:
    # TODO: Quickfix guided by https://stackoverflow.com/questions/63714223/correct-type-annotation-for-a-celery-task
    from celery.task import Task
    from celery.local import PromiseProxy

    CELERY_TASK_TYPE = Union[Task, PromiseProxy]
else:
    CELERY_TASK_TYPE = Any


class Daemon:

    @staticmethod
    def summon(name: str, publisher: CELERY_TASK_TYPE, **heart_configs):
        def decorator(worker: CELERY_TASK_TYPE):
            def wrapper(*args, **kwargs):
                # Initialize the daemon and broadcast heartbeat
                daemon = Daemon(name=name, publisher=publisher, **heart_configs)
                daemon.broadcast()
                # Execute the worker function
                output = worker.delay(*args, **kwargs)
                # Kill the daemon
                daemon.kill()
                return output
            return wrapper
        return decorator

    def __init__(
            self,
            name: str,
            publisher: CELERY_TASK_TYPE,
            **heart_configs
    ):
        self.name = name
        self.publisher = publisher
        self.broadcast_thread: Optional[Thread] = None
        self.heart = DaemonHeart.beat(
            app_name=name,
            **{  # type: ignore
                "mode": DaemonHeart.Mode.MONITOR,
                "enable_beat_logs": True,
                "enable_pulse_monitor": True,
                "pulse_monitor_frequency": None,
                "pulse_monitor_sensibility_factor": 1.5,
                **heart_configs
            }
        )

    def kill(self):
        # Stop heart
        self.heart.stroke()
        self.heart.join()
        self.heart.close()
        # Stop broadcast
        self.broadcast_thread.join() if self.broadcast_thread is not None else None

    def broadcast(self):
        self.broadcast_thread: Thread = Thread(
            target=lambda: self._broadcast(),
            daemon=True
        )
        self.broadcast_thread.start()

    def _broadcast(self):
        while not self.heart.no_pulse.is_set():
            payload = self.heart.queue_beat_logs.get(block=True)
            self.publisher.delay(**payload)
