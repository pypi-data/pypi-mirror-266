from shutil import get_terminal_size


class LoggerBase:
    _logging_width: int = None

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
