import logging
from types import TracebackType
from typing import Any, Optional, Type

from typing_extensions import Self

from faststream.broker.middlewares.base import BaseMiddleware
from faststream.exceptions import IgnoredException
from faststream.types import DecodedMessage, LoggerProto
from faststream.utils.context.repository import context


class CriticalLogMiddleware(BaseMiddleware):
    """A middleware class for logging critical errors."""

    def __init__(
        self,
        logger: Optional[LoggerProto],
        log_level: int,
    ) -> None:
        """Initialize the class."""
        self.logger = logger
        self.log_level = log_level

    def __call__(self, *args: Any) -> Self:
        """Call the object with a message."""
        return self

    async def on_consume(
        self,
        msg: Optional[DecodedMessage],
    ) -> Optional[DecodedMessage]:
        if self.logger is not None:
            c = context.get_local("log_context") or {}
            self.logger.log(self.log_level, "Received", extra=c)

        return await super().on_consume(msg)

    async def after_processed(
        self,
        exc_type: Optional[Type[BaseException]] = None,
        exc_val: Optional[BaseException] = None,
        exc_tb: Optional[TracebackType] = None,
    ) -> bool:
        """Asynchronously called after processing."""
        if self.logger is not None:
            c = context.get_local("log_context") or {}

            if exc_type:
                if issubclass(exc_type, IgnoredException):
                    self.logger.log(
                        logging.INFO,
                        exc_val,
                        extra=c,
                    )
                else:
                    self.logger.log(
                        logging.ERROR,
                        f"{exc_type.__name__}: {exc_val}",
                        exc_info=exc_val,
                        extra=c,
                    )

            self.logger.log(self.log_level, "Processed", extra=c)

        await super().after_processed(exc_type, exc_val, exc_tb)

        if exc_type:
            return not issubclass(exc_type, (IgnoredException, SystemExit))

        return False
