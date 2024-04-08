from dataclasses import dataclass

from envo import logger
from envo.utils import Callback


class Status:
    @dataclass
    class Callbacks:
        on_ready: Callback
        on_not_ready: Callback

    _context_ready: bool
    _source_ready: bool

    def __init__(self, calls: Callbacks) -> None:
        self.calls = calls
        self._context_ready = False
        self._source_ready = False

    def __repr__(self) -> str:
        return (
            f"Status (context_ready={self.shell_context_ready}, source_ready={self._source_ready})"
        )

    @property
    def shell_context_ready(self) -> bool:
        return self._context_ready

    @shell_context_ready.setter
    def shell_context_ready(self, value: bool) -> None:
        self._context_ready = value
        logger.debug("Context", {"ready": value})
        self._on_status_change()

    @property
    def source_ready(self) -> bool:
        return self._source_ready

    @source_ready.setter
    def source_ready(self, value: bool) -> None:
        self._source_ready = value
        logger.debug("Source", {"ready": value})
        self._on_status_change()

    @property
    def ready(self) -> bool:
        return self.shell_context_ready and self.source_ready

    def _on_status_change(self) -> None:
        if self.ready:
            logger.debug("Everything ready")
            self.calls.on_ready()
        else:
            logger.debug(f"Not ready {repr(self)}")
            self.calls.on_not_ready()
