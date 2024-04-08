import os
import enum
from dataclasses import dataclass
from typing import Optional

from rhdzmota.settings import logger_manager, Env


logger = logger_manager.get_logger(name=__name__)


@dataclass(frozen=True, slots=True)
class SentrySDKConfig:
    overwrite_environ_key_dsn: Optional[str] = None
    overwrite_environ_key_traces: Optional[str] = None
    overwrite_environ_key_profiles: Optional[str] = None
    overwrite_environ_key_disable_tracing: Optional[str] = None
    overwrite_default_val_traces: Optional[str] = None
    overwrite_default_val_profiles: Optional[str] = None
    overwrite_default_val_disable_tracing: Optional[str] = None

    @classmethod
    def configure_with_defaults(cls) -> bool:
        logger.info("Configuring SentrySDK with defaults...")
        return cls().configure()

    def configure(self) -> bool:
        if not self.dsn:
            return False
        import sentry_sdk

        return sentry_sdk.init(
            dsn=self.dsn,
            enable_tracing=not self.disable_tracing,
            traces_sample_rate=self.traces_sample_rate,
            profiles_sample_rate=self.profiles_sample_rate,
        ) or True

    @property
    def dsn(self) -> Optional[str]:
        environ_key = self.overwrite_environ_key_dsn or "SENTRY_SDK_DSN"
        return Env.get(
            name=environ_key,
            default=None,
            enforce=False,
        )

    @property
    def disable_tracing(self) -> bool:
        """
        Disable Performance Monitoring
        """
        environ_key = self.overwrite_environ_key_disable_tracing or "SENTRY_SDK_DISABLE_TRACING"
        return bool(int(Env.get(
            name=environ_key,
            default=self.overwrite_default_val_disable_tracing or "0",
            enforce=False,
        )))

    @property
    def traces_sample_rate(self) -> float:
        """
        Traces Sample Rate
        A value of 1.0 is equivalent to capturing 100% of the transactions
        for performance monitoring.
        """
        environ_key = self.overwrite_environ_key_traces or "SENTRY_SDK_SAMPLING_RATE_TRACES"
        value = float(Env.get(
            name=environ_key,
            default=self.overwrite_default_val_traces or "1.0",
            enforce=False,
        ))
        if 0 < value <= 1:
            return value
        raise ValueError("Invalid value ({value}) for config: {environ_key}")

    @property
    def profiles_sample_rate(self) -> float:
        """
        Profiles Sample Rate
        A value of 1.0 is equivalent to profiling 100% of sampled transactions.
        """
        environ_key = self.overwrite_environ_key_profiles or "SENTRY_SDK_SAMPLING_RATE_PROFILES"
        value = float(Env.get(
            name=environ_key,
            default=self.overwrite_default_val_profiles or "1.0",
            enforce=False,
        ))
        if 0 < value <= 1:
            return value
        raise ValueError("Invalid value ({value}) for config: {environ_key}")
