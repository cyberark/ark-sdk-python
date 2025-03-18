import random
import time
from functools import partial
from typing import Any, Callable, Optional, Tuple, Type


class ArkRetry:
    @staticmethod
    def __retry_internal(
        f: Callable,
        exceptions: Tuple[Type[BaseException]] = Exception,
        tries: int = -1,
        delay: int = 0,
        max_delay: Optional[int] = None,
        backoff: int = 1,
        jitter: int = 0,
        logger: Optional[Any] = None,
    ) -> Any:
        _tries, _delay = tries, delay
        while _tries:
            try:
                return f()
            except exceptions as e:
                _tries -= 1
                if not _tries:
                    raise

                if logger is not None:
                    logger.warning('%s, retrying in %s seconds...', e, _delay)

                time.sleep(_delay)
                _delay *= backoff

                if isinstance(jitter, tuple):
                    _delay += random.uniform(*jitter)
                else:
                    _delay += jitter

                if max_delay is not None:
                    _delay = min(_delay, max_delay)

    @staticmethod
    def retry_call(
        f: Callable,
        fargs: Any = None,
        fkwargs: Any = None,
        exceptions: Tuple[Type[BaseException]] = Exception,
        tries: int = -1,
        delay: int = 0,
        max_delay: Optional[int] = None,
        backoff: int = 1,
        jitter: int = 0,
        logger: Optional[Any] = None,
    ) -> Any:
        args = fargs if fargs else list()
        kwargs = fkwargs if fkwargs else dict()
        return ArkRetry.__retry_internal(
            partial(f, *args, **kwargs),
            exceptions,
            tries,
            delay,
            max_delay,
            backoff,
            jitter,
            logger,
        )
