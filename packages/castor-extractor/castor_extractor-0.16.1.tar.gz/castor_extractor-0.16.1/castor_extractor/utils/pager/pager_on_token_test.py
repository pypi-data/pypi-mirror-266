from typing import Any, Callable, Dict, List, Optional

from .pager_on_token import PagerOnToken

ITEMS = list(range(1000))

OStr = Optional[str]


def _make_callback_with_token(
    elements: List[Dict[str, str]],
) -> Callable[[OStr, int], Dict[str, Any]]:
    def _callback(page_token: OStr, per_page: int) -> Dict[str, Any]:
        """callable with a token that indicates how to retrieve the next page"""
        if page_token:
            _start = int(page_token)
        else:
            _start = 0
        _end = _start + per_page
        return {"res": elements[_start:_end], "next_page_token": str(_end)}

    return _callback


def _make_callback_with_missing_token(
    elements: List[Dict[str, str]],
) -> Callable[[OStr, int], Dict[str, Any]]:
    def _callback(page_token: OStr, per_page: int) -> Dict[str, Any]:
        """callable with a token that indicates how to retrieve the next page
        except for the last page"""
        if page_token:
            _start = int(page_token)
        else:
            _start = 0
        _end = _start + per_page
        if _end == len(ITEMS):
            return {"res": elements[_start:_end]}
        return {"res": elements[_start:_end], "next_page_token": str(_end)}

    return _callback


def test_pagerontoken__all():
    """unit test for PagerOnToken#all()"""
    pager = PagerOnToken(_make_callback_with_token(ITEMS))
    # When no argument provided
    assert pager.all() == ITEMS
    # When per page is less than the number of ITEMS
    assert pager.all(per_page=1) == ITEMS
    # When per page is more than the number of ITEMS
    assert pager.all(per_page=len(ITEMS) + 20) == ITEMS

    # Same test suite, but no token is provided at the last call
    pager = PagerOnToken(_make_callback_with_missing_token(ITEMS))
    # When no argument provided
    assert pager.all() == ITEMS
    # When per page is less than the number of ITEMS
    assert pager.all(per_page=1) == ITEMS
    # When per page is more than the number of ITEMS
    assert pager.all(per_page=len(ITEMS) + 20) == ITEMS


def test_pagerontoken__iterator__pagination():
    """unit test for PagerOnToken#iterator() (pagination)"""
    pager = PagerOnToken(_make_callback_with_token(ITEMS))

    def nb_of_pages(per_page: int) -> int:
        return len([page for page in pager.iterator(per_page=per_page)])

    assert nb_of_pages(per_page=len(ITEMS)) == 1
    assert nb_of_pages(per_page=1) == len(ITEMS)
    assert nb_of_pages(per_page=2) == len(ITEMS) // 2
    assert nb_of_pages(per_page=4) == len(ITEMS) // 4
