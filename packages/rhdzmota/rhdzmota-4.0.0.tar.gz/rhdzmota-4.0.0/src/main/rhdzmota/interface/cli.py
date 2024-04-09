import json
import time
import datetime as dt
from typing import Optional

from rhdzmota.settings import (
    get_environ_variable,
    logger_manager,
)


logger = logger_manager.get_logger(name=__name__)


class CLIBase:

    class Formatter:

        def __init__(self, cls: Optional = None, default: Optional = None, serialize: bool = None):  # type: ignore
            self.serialize = serialize
            self.serializer = lambda obj: json.dumps(obj, cls=cls, default=default, indent=4)

        def __call__(self, method):
            def wrapper(other, *args, **kwargs):
                output = method(other, *args, **kwargs)
                if not self.serialize:
                    return output
                if not isinstance(output, str):
                    output = self.serializer(output)
                return output
            return wrapper

    def __init__(
            self,
            extension_import_pattern: Optional[str] = None,
    ):
        self.extension_import_pattern = extension_import_pattern
        self.now = dt.datetime.utcnow().isoformat()
        self.start = time.perf_counter()
        self.end = None

    def standard_version_import_pattern(self) -> str:
        *base_imports, _ = self.extension_import_pattern.split(".")
        return ".".join(base_imports) + "_version"

    def version(
            self,
            overwrite_version_import_pattern: Optional[str] = None,
            overwrite_version_varname: Optional[str] = None,
            path: bool = False,
            fail: bool = False,
    ):
        import importlib

        version_varname = overwrite_version_varname or "version"
        version_import_pattern = overwrite_version_import_pattern or \
            self.standard_version_import_pattern()
        version_module = importlib.import_module(version_import_pattern)
        version = getattr(version_module, version_varname)
        if not version and fail:
            raise ValueError(
                f"Version ({version_varname}) not found: {version_import_pattern}"
            )
        return version.filepath if path else version.value

    def now(self, local: bool = False) -> str:
        return (dt.datetime.utcnow() if not local else dt.datetime.now()).isoformat()

    def hello(
            self,
            recipient: Optional[str] = None,
            sleep: int = 1,
            delegate: bool = False,
    ):
        import time

        recipient = recipient or "world"
        if sleep:
            time.sleep(sleep)
        try:
            from rhdzmota.celery_workers.hello import worker
            if delegate:
                return worker.delay(name=recipient)
        except ImportError:
            return f"Hello, {recipient}!"

    def on_start(self):
        logger.info("CLI Method not implemented: on_start")

    def on_finalize(self):
        logger.info("CLI method not implemented: on_finalize")

    def __enter__(self) -> 'CLIBase':
        self.on_start()
        return self

    def __exit__(self, *args):
        self.on_finalize()
        self.end = time.perf_counter()
        logger.info(f"Command Start Timestamp: {self.now}")
        logger.info(f"Command Duration: {self.end - self.start}")

    @Formatter()
    def environ(self, name: str) -> Optional[str]:
        return get_environ_variable(
            name=name,
            enforce=False,
        )
