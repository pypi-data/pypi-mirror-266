import logging
from shutil import get_terminal_size

# create a default_logger for testers
default_logger = logging.getLogger('lineartest_logger')
default_logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
handler.setFormatter(formatter)
default_logger.addHandler(handler)


class LoggerBase:
    _logging_width: int = None
    logger: logging.Logger = default_logger

    def info(self, msg, *args, **kwargs):
        """Pass the arguments to `self.default_logger` if specified."""
        if self.logger:
            self.logger.info(msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        """Pass the arguments to `self.default_logger` if specified."""
        if self.logger:
            self.logger.warning(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        """Pass the arguments to `self.default_logger` if specified."""
        if self.logger:
            self.logger.error(msg, *args, **kwargs)

    @property
    def logging_width(self) -> int:
        """Retrieve the logging width."""
        if self._logging_width:
            return self._logging_width
        size = get_terminal_size(fallback=(60, 24))
        return size.columns

    @classmethod
    def set_logging_width(cls, value: int | None):
        cls._logging_width = value


def set_logging_width(value: int | None):
    LoggerBase.set_logging_width(value)
