from typing import Any, Callable, Dict, Iterator, Optional, Sequence, TypeVar

from .pager import (
    DEFAULT_PER_PAGE,
    AbstractPager,
    PagerLogger,
    PagerStopStrategy,
)

T = TypeVar("T")


class PagerOnToken(AbstractPager):
    """Token-based pagination"""

    def __init__(
        self,
        callback: Callable[[Optional[str], Optional[int]], Dict[Any, Any]],
        *,
        logger: Optional[PagerLogger] = None,
        start_page: int = 1,
        stop_strategy: PagerStopStrategy = PagerStopStrategy.EMPTY_PAGE,
    ):
        self._callback = callback
        self._logger = logger or PagerLogger()
        self._start_page = start_page
        self._stop_strategy = stop_strategy

    def iterator(
        self,
        per_page: int = DEFAULT_PER_PAGE,
    ) -> Iterator[Sequence[T]]:
        """Yields data provided by the callback as a list using the nexttoken"""
        stop_on_empty_page = self._stop_strategy == PagerStopStrategy.EMPTY_PAGE
        page = self._start_page
        total_results = 0
        page_token = None
        while True:
            results = self._callback(page_token, per_page)
            nb_results = len(results.get("res", []))
            total_results += nb_results

            if results.get("res"):
                yield results["res"]

            stop = self.should_stop(nb_results, per_page, stop_on_empty_page)
            page_token = results.get("next_page_token")
            if stop or not page_token:
                break
            page += 1

        self._logger.on_success(page, total_results)
