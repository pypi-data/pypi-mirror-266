import time
import enum
import datetime as dt
from typing import Optional
from dataclasses import dataclass
from multiprocessing import Event, Queue, Process, Value
from threading import Thread

from ..utils.runtime import system_describe


class DaemonHeart(Process):
    _beats = Value("i", 0)
    _last_beat_timestamp = Value("i", 0)
    no_pulse = Event()
    queue_terminate: Queue = Queue()
    queue_beat_logs: Queue = Queue()

    @dataclass
    class PulseMonitor:
        status: 'DaemonHeart.PulseMonitor.Status'
        checks: int = 0
        last_check: Optional[dt.datetime] = None

        class Status(enum.Enum):
            ACTIVE = 1
            ON_GOING = 2
            DONE = 3

    class Mode(enum.Enum):
        MINIMAL = "MINIMAL"
        MONITOR = "MONITOR"

    def __init__(
            self,
            app_name: str,
            interval: int = 3,
            mode: Mode = Mode.MINIMAL,
            enable_beat_logs: bool = False,
            max_qsize_beat_logs: Optional[int] = 1000,
            non_daemon: bool = False,
    ):
        self.app_name = app_name
        self.interval = interval
        self.enable_beat_logs = enable_beat_logs
        self.mode = mode
        self.max_qsize_beat_logs: Optional[int] = max_qsize_beat_logs
        self.pulse_monitor: Optional[DaemonHeart.PulseMonitor] = None
        self.pulse_monitor_thread: Optional[Thread] = None
        super().__init__(daemon=not non_daemon)

    @property
    def beats(self) -> int:
        return self._beats.value

    @property
    def last_beat_timestamp(self) -> int:
        return self._last_beat_timestamp.value

    def last_beat_seconds_ago(self):
        return dt.datetime.utcnow().timestamp() - self.last_beat_timestamp

    def has_pulse(self, sensibility_factor: float = 1.5) -> bool:
        return self.last_beat_seconds_ago() <= sensibility_factor * self.interval

    def run(self):
        while not self.queue_terminate.qsize():
            # Heartbeat payload
            now = dt.datetime.utcnow()
            payload = {
                "app_name": self.app_name,
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "created_at": int(now.timestamp()),
                "heartbeat_index": self.beats,
                "heartbeat_mode": self.mode.name,
                "heartbeat_approx_seconds_diff": 0 if self.beats == 0 else self.last_beat_seconds_ago()
            }
            if self.mode is self.Mode.MONITOR:
                payload = {
                    **payload,
                    **system_describe()
                }
            if self.enable_beat_logs:
                # Send description to logs queue
                self.queue_beat_logs.put(payload)
                # Keep queue at the requested maximum size.
                max_qsize_is_set = isinstance(self.max_qsize_beat_logs, int) and self.max_qsize_beat_logs > 0
                if max_qsize_is_set and self.unacknowledged_beats() >= self.max_qsize_beat_logs:
                    self.queue_beat_logs.get()
            # Increase the beat count & metadata
            with self._beats.get_lock():
                self._beats.value += 1
            with self._last_beat_timestamp.get_lock():
                self._last_beat_timestamp.value = payload["created_at"]
            # Wait for next beat
            time.sleep(self.interval)

    def unacknowledged_beats(self) -> int:
        if not self.enable_beat_logs:
            raise ValueError(
                "This method can only be access when the beat-logs are enabled (i.e. enable_beat_logs is set to True)"
            )
        return self.queue_beat_logs.qsize()

    @classmethod
    def stroke(cls):
        cls.queue_terminate.put("TERMINATE")

    def pulse_monitor_worker(self, sensibility_factor: float = 1.5, frequency: Optional[int] = None):
        frequency = frequency or int(self.interval / 2)
        time.sleep(self.interval)
        if self.pulse_monitor is None:
            raise ValueError("Cannot call the pulse_monitor_worker without a pulse_monitor instance.")
        self.pulse_monitor.status = DaemonHeart.PulseMonitor.Status.ON_GOING
        while self.has_pulse(sensibility_factor=sensibility_factor):
            self.pulse_monitor.checks += 1
            self.pulse_monitor.last_check = dt.datetime.utcnow()
            time.sleep(frequency)
        # Set the no-pulse event
        self.pulse_monitor.status = DaemonHeart.PulseMonitor.Status.DONE
        self.no_pulse.set()

    def enable_pulse_monitor(self, sensibility_factor: float = 1.5, frequency: Optional[int] = None):
        self.pulse_monitor = DaemonHeart.PulseMonitor(status=DaemonHeart.PulseMonitor.Status.ACTIVE)
        self.pulse_monitor_thread = Thread(
            target=lambda: self.pulse_monitor_worker(
                sensibility_factor=sensibility_factor,
                frequency=frequency,
            ),
            daemon=True,
        )
        self.pulse_monitor_thread.start()

    @classmethod
    def beat(
            cls,
            app_name: str,
            interval: int = 3,
            mode: Mode = Mode.MINIMAL,
            enable_beat_logs: bool = False,
            enable_pulse_monitor: bool = False,
            max_qsize_beat_logs: Optional[int] = 1000,
            pulse_monitor_sensibility_factor: float = 1.5,
            pulse_monitor_frequency: Optional[int] = None,
            non_daemon: bool = False,
    ):
        # DaemonHeart
        instance = cls(
            app_name=app_name,
            interval=interval,
            mode=mode,
            enable_beat_logs=enable_beat_logs,
            max_qsize_beat_logs=max_qsize_beat_logs,
            non_daemon=non_daemon,
        )
        instance.start()

        # Pulse Monitor
        instance.enable_pulse_monitor(
            sensibility_factor=pulse_monitor_sensibility_factor,
            frequency=pulse_monitor_frequency,
        ) if enable_pulse_monitor else None

        return instance

    @classmethod
    def beat_mode_minimal(
            cls,
            app_name: str,
            interval: int = 3,
            enable_beat_logs: bool = False,
            enable_pulse_monitor: bool = False,
            pulse_monitor_sensibility_factor: float = 1.5,
            pulse_monitor_frequency: Optional[int] = None,
            **kwargs
    ) -> 'DaemonHeart':
        return cls.beat(
            app_name=app_name,
            interval=interval,
            enable_beat_logs=enable_beat_logs,
            enable_pulse_monitor=enable_pulse_monitor,
            pulse_monitor_frequency=pulse_monitor_frequency,
            pulse_monitor_sensibility_factor=pulse_monitor_sensibility_factor,
            mode=cls.Mode.MINIMAL,
            **kwargs
        )

    @classmethod
    def beat_mode_monitor(
            cls,
            app_name: str,
            interval: int = 3,
            enable_pulse_monitor: bool = False,
            pulse_monitor_sensibility_factor: float = 1.5,
            pulse_monitor_frequency: Optional[int] = None,
            max_qsize_beat_logs: Optional[int] = 1000,
            **kwargs
    ) -> 'DaemonHeart':
        return cls.beat(
            app_name=app_name,
            interval=interval,
            mode=cls.Mode.MONITOR,
            enable_beat_logs=True,
            enable_pulse_monitor=enable_pulse_monitor,
            pulse_monitor_frequency=pulse_monitor_frequency,
            pulse_monitor_sensibility_factor=pulse_monitor_sensibility_factor,
            max_qsize_beat_logs=max_qsize_beat_logs,
            **kwargs,
        )
