"""Define utility functions for working with lists.
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


def diminish(list_a: list, *, wrt: list) -> None:
    """Diminish the first given list with respect the second one, in place. Similar to
    get_common_elements, which see. After this call, the first given list (list_a) will contain
    only those elements in the original list that are also present in the second list (wrt).
    Non-commutative.
    """
    a_ = [i for i in list_a]  # local copy
    for i in a_:
        if i in wrt:
            continue
        else:
            list_a.pop(list_a.index(i))


def filter_by_index(lst: list[list], indexes: list[int]):
    """Receives a list of lists and returns a list of lists except the returned sublist elements
    are selected by index. Parameter indexes provides the selected indexes."""
    return [[j[i] for i in indexes] for j in lst]


def get_all_pairs(given: list) -> list[tuple]:
    """Return a list of all possible unordered pairs of the elements in the given list.

    Example:
        planets = ["sun", "mercury", "venus", "earth"]
        get_all_pairs(planets)

        1...... ('sun', 'mercury')
        2...... ('sun', 'venus')
        3...... ('sun', 'earth')
        4...... ('mercury', 'venus')
        5...... ('mercury', 'earth')
        6...... ('venus', 'earth')
    """
    pairs = []
    for i in range(len(given) - 1):
        sublist = given[i + 1 :]
        for j in sublist:
            pairs.append((given[i], j))
    return pairs


def get_common_elements(list_a: list, list_b: list) -> list:
    """Return a list of elements that are present in both of the given lists. Similar to
    diminish, which changes the first list in place. Commutative."""
    return list(set([i for i in list_a if i in list_b]))


def get_duplicates(list_a: list) -> list:
    """Return a list of the elements that appear at least twice in the given list."""
    if not has_duplicates(list_a):
        return []

    duplicates = set()
    seen = set()

    for i in list_a:
        if i not in seen:
            seen.add(i)
        else:
            duplicates.add(i)

    return list(set(duplicates))


def get_first_not_none_from_end(list_: list) -> Any | None:
    """Return the first element in the given list that is not None starting from the end of the
    list. If there is not such element, return None."""
    list_ = [i for i in list_ if i is not None]
    if len(list_) > 0:
        return list_[-1]


def get_first_not_none_from_start(list_: list) -> Any | None:
    """Return the first element in the given list that is not None starting from the beginning of
    the list."""
    list_ = [i for i in list_ if i is not None]
    if len(list_) > 0:
        return list_[0]


def get_missing_elements(list_a: list, *, wrt: list) -> list:
    """Return a list of the elements in first list that are missing from the second list.
    Non-commutative."""
    return list(set(list_a) - set(wrt))


def get_smaller_lists(given: list, *, max_items: int) -> list[list]:
    """Divide the given list into smaller lists, each with max_items or less.
    """
    num_items = len(given)

    if num_items <= max_items or 0 >= max_items:
        logger.warning(
            f"Received <<num_keys>> = {num_items}, <<max_keys>> = {max_items}. Nothing "
            f"to do. Returning an empty list."
        )
        return []

    return [given[i : i + max_items] for i in range(0, num_items, max_items)]


def get_string(
    list_: list, end_line: bool = False, delimiter: str | None = None
) -> str:
    """Convert the given list to a string."""
    delimiter = ", " if delimiter is None else delimiter
    string = delimiter.join([str(i) if not isinstance(i, str) else i for i in list_])
    if end_line and not string.endswith("\n"):
        string += "\n"
    return string


def has_duplicates(list_: list) -> bool:
    """Return True if any element of the given list (assumed flat) is duplicated."""
    return len(list_) != len(set(list_))


def scalar_multiply(c: int | float, l_: list) -> list:
    """Multiply each element of the given list by <c> and return the new list."""
    return [c * i for i in l_]


def vector_add(l_: list[list]) -> list:
    """Return a list where each element is the element-wise sum of the given lists, which must
    all be of the same length."""
    return [sum(i) for i in zip(*l_)]
