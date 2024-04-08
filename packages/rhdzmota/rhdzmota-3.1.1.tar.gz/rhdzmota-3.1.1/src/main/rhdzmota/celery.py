from celery import Celery

from .heartbeat.daemon import Daemon
from .settings import (
    RHDZMOTA_CELERY_BROKER_HOST,
    RHDZMOTA_DAEMON_NAME
)


# Celery application instance
app = Celery(
    "tasks",
    broker=f"redis://{RHDZMOTA_CELERY_BROKER_HOST}",
    backend=f"redis://{RHDZMOTA_CELERY_BROKER_HOST}",
)

app.conf.update(
    task_routes={
        "rhdzmota.celery.daemon_heartbeat_publisher": {
            "queue": "queue_heartbeat"
        }
    }
)


@app.task
def daemon_heartbeat_publisher(**kwargs):
    print(kwargs)


# Daemon instance
if RHDZMOTA_DAEMON_NAME:
    daemon = Daemon(name=RHDZMOTA_DAEMON_NAME, publisher=daemon_heartbeat_publisher, interval=3)
    daemon.broadcast()
