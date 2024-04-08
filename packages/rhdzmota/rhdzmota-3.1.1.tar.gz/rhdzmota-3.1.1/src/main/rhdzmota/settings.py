import os
import enum
import logging
from typing import Callable, Dict, Literal, NoReturn, Optional, Union, TypeVar, overload
from logging.config import dictConfig

T = TypeVar("T")


@overload
def get_environ_variable(
        name: str,
        default: Literal[None] = None,
        enforce: bool = False,
        apply: Optional[Callable[[Optional[str]], T]] = None,
) -> Optional[Union[str, T]]:
    ...


@overload
def get_environ_variable(
        name: str,
        default: str,
        enforce: bool = False,
        apply: Optional[Callable[[str], T]] = None,
) -> Union[str, T]:
    ...


def get_environ_variable(
        name: str,
        default: Optional[str] = None,
        enforce: bool = False,
        apply: Optional[Union[Callable[[Optional[str]], T], Callable[[str], T]]] = None,
) -> Optional[Union[Optional[str], T]]:
    return (apply or (lambda x: x))(  # type: ignore
        os.environ.get(name, default=default) if not enforce else  # type: ignore
        os.environ.get(name) or (lambda: (_ for _ in ())
                                 .throw(ValueError(f"Missing environ variable: {name}")))()
    )


class Env(enum.Enum):
    DEFAULT_PYTHON_HANDLER_LEVEL = get_environ_variable(
        name="DEFAULT_PYTHON_HANDLER_LEVEL",
        default="INFO",
    )

    @staticmethod
    def get(
            name: str,
            default: Optional[str] = None,
            enforce: bool = False,
    ) -> str:
        return get_environ_variable(
            name=name,
            default=default,
            enforce=enforce,
        )


# Logger configuration
default_logger_configuration = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": get_environ_variable(
                name="DEFAULT_PYTHON_LOGGER",
                default="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            )
        },
    },
    "handlers": {
        "default": {
            "level": get_environ_variable(
                name="DEFAULT_PYTHON_HANDLER_LEVEL",
                default="INFO"
            ),
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": [
                "default"
            ],
            "level": get_environ_variable(
                name="DEFAULT_PYTHON_LOGGER_LEVEL",
                default="INFO",
            ),
            "propagate": True
        }
    }
}


def configure_logger_callable(config_dictionary: Optional[Dict] = None) -> Callable:
    def get_logger(name: str):
        dictConfig(config_dictionary or default_logger_configuration)
        return logging.getLogger(name)
    return get_logger


class LoggerManager:
    class _Singleton:
        count: int = 0
        value: Optional['LoggerManager'] = None

    def __new__(cls, *args, **kwargs):
        if cls._Singleton.count == 0:
            instance = super(LoggerManager, cls).__new__(cls)
            cls._Singleton.count += 1
            cls._Singleton.value = instance
            return instance
        return cls._Singleton.value

    def __init__(self, config_dictionary: Optional[Dict] = None, disable_singleton: bool = False):
        self.config_dictionary: Dict = config_dictionary or default_logger_configuration

        if not disable_singleton and self._Singleton.count > 0:
            return
        self._Singleton.count += 1
        self._Singleton.value = self

    def set_configuration(self, **kwargs):
        self.config_dictionary = kwargs

    def get_logger(self, name: str, overwrite_config_dictionary: Optional[Dict] = None):
        dictConfig(overwrite_config_dictionary or self.config_dictionary)
        return logging.getLogger(name)

    @classmethod
    def singleton(cls, overwrite_config_dictionary: Optional[Dict] = None) -> 'LoggerManager':
        if overwrite_config_dictionary or cls._Singleton.value is None:
            cls._Singleton.value = cls(overwrite_config_dictionary)
            if cls._Singleton.count > 1:
                cls._Singleton.value.get_logger(name=__name__).warning("Creating a new logger manager instance.")
        return cls._Singleton.value


logger_manager = LoggerManager.singleton()
logger = logger_manager.get_logger(name=__name__)

# Celery

RHDZMOTA_CELERY_BROKER_HOST = get_environ_variable(
    name="RHDZMOTA_CELERY_BROKER_HOST",
    default="127.0.0.1"
)

# Daemon
RHDZMOTA_DAEMON_NAME = get_environ_variable(
    name="RHDZMOTA_DAEMON_NAME",
)

# Mail

EMAIL_SERVER_LOGIN_USER = get_environ_variable(
    name="EMAIL_SERVER_LOGIN_USER",
)

EMAIL_SERVER_LOGIN_PASSWORD = get_environ_variable(
    name="EMAIL_SERVER_LOGIN_PASSWORD",
)

# JWT

JWT_ENCRYPTION_ALGORITHM: str = get_environ_variable(
    name="JWT_ENCRYPTION_ALGORITHM",
    default="HS256"
)


def _get_default_jwt_secret_key() -> str:
    logger.warning("Using the default JWT Secret Key.")
    return "default"


def get_jwt_secret_key() -> str:
    return get_environ_variable(name="JWT_SECRET_KEY") or _get_default_jwt_secret_key()
