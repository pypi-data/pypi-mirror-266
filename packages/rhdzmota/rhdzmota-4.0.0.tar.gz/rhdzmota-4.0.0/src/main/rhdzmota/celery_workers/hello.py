
from ..celery import app


@app.task
def worker(name: str) -> str:
    return f"Hello, {name or 'world'}!"
