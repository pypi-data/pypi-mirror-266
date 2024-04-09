import inspect
import traceback
from collections.abc import Callable
from typing import Annotated, Any, ParamSpec, TypeVar, get_args, get_origin

from ._log import LoggerBase

P = ParamSpec('P')
T = TypeVar('T')


class Schedule(LoggerBase):
    """The class managing testing schedules."""

    def __init__(self, get_by_keyword: bool = False):
        """
        Initialize the `Schedule` instance.
        :param get_by_keyword: whether to get by keyword or not
        """
        super().__init__()
        self._schedule = []
        self._data = {}
        self._get_by_keyword = get_by_keyword

    def get(self, key: str | Callable, get_by_keyword: bool | None = None) -> Any:
        """
        Retrieve the return value of a finished step.
        :param key: the name of the step or the function itself
        :param get_by_keyword: whether to get by keyword or not
        :return: the return value of the finished step
        """
        # return if the key is the function itself
        if isinstance(key, Callable):
            return self._data[key]

        # raise a TypeError if key is neither a function nor a string
        if not isinstance(key, str):
            raise TypeError(
                f'expected a function or a string, got {type(key).__name__} instead.'
            )

        # try to find a function named after the key
        for func, value in self._data.items():
            if func.__name__ == key:
                return value

        # try to search the function name by key as a keyword
        if get_by_keyword or self._get_by_keyword:
            for func, value in self._data.items():
                if key in func.__name__:
                    return value

        # get nothing and raise a KeyError
        raise KeyError(key)

    def __call__(self, func: Callable[P, T]) -> Callable[P, T]:
        """
        Decorator to add a function to the sch.
        :param func: the function to add
        :return: the function itself
        """
        self._schedule.append(func)
        return func

    def _exec(self, func: Callable, *args, **kwargs):
        def get_real_type(type_hint: Any) -> Any:
            """Retrieve the real type of a parameter type hint."""
            if isinstance(type_hint, type):
                if get_origin(type_hint) == Annotated:
                    return get_real_type(get_args(type_hint)[0])
                else:
                    return type_hint.__name__
            else:
                return type_hint

        # args and kwargs actually passed
        real_args = []
        real_kwargs = {}

        # traverse the function signature
        positional_allowed = True  # allow using positonal argument as keyword argument
        current = 0  # current index of positonal argumentss
        for name, para in inspect.signature(func).parameters.items():
            required = para.default is para.empty  # whether the argument is requried
            if para.kind == para.POSITIONAL_ONLY:
                try:
                    # append the positional argument
                    real_args.append(args[current])
                    current += 1
                except IndexError:
                    if not required:
                        # missing required positional argument
                        raise TypeError(
                            f'{func.__name__}() missing required positional argument: {name}'
                        )
            elif para.kind == para.POSITIONAL_OR_KEYWORD:
                if name in kwargs:
                    real_kwargs[name] = kwargs[name]
                elif positional_allowed:
                    try:
                        real_kwargs[name] = args[current]
                        current += 1
                    except IndexError:
                        if required:
                            # missing required positional argument
                            raise TypeError(
                                f'{func.__name__}() missing required positional argument: {name}'
                            )
                else:
                    # missing required positional argument
                    raise TypeError(
                        f'{func.__name__}() missing required positional argument: {name}'
                    )
            elif para.kind == para.KEYWORD_ONLY:
                if name in kwargs:
                    real_kwargs[name] = kwargs[name]
                else:
                    # missing required keyword argument
                    raise TypeError(
                        f'{func.__name__}() missing required keyword-only argument: {name}'
                    )

        # execute the function
        self._data[func] = func(*real_args, **real_kwargs)

    def run(self, *args, **kwargs) -> bool:
        """
        Run the schedules.
        :param args: the positonal arguments to be passed to the schedules
        :param kwargs: the keyword arguments to be passed to the schedules
        :return: whether the schedules are executed successfully
        """
        total = len(self._schedule)
        success = True

        for index, func in enumerate(self._schedule):
            # log the start of the schedule
            self.info(
                f' SCHEDULE START ({index+1}/{total}): {func.__name__} '.center(
                    self.logging_width, '='
                )
            )

            # execute the schedule
            try:
                self._exec(func, *args, **kwargs)
            except Exception as e:
                self.info('')
                self.info(
                    f' ERROR: {e.__class__.__name__} '.center(self.logging_width, '-')
                )
                self.error(traceback.format_exc())
                self.info(
                    f' SCHEDULE ABORT ({index+1}/{total}): {func.__name__} '.center(
                        self.logging_width, '='
                    )
                )
                success = False
                break

            # log the end of the schedule
            self.info(
                f' SCHEDULE END ({index+1}/{total}): {func.__name__} '.center(
                    self.logging_width, '='
                )
            )
            self.info('')

        return success
