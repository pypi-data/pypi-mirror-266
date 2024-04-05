import logging

from kink import di

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyautowire.injectable import Injectable


def register(injectable: "Injectable") -> "Injectable":
    di[injectable.get_fully_qualified_name()] = injectable

    return injectable


def contains(injectable: "Injectable") -> bool:
    lookup_result = injectable.get_fully_qualified_name() in di
    logging.debug(
        f"Checking if injectable {injectable.get_fully_qualified_name()} is in cache: {lookup_result}"
    )
    return lookup_result


def get(injectable: "Injectable") -> "Injectable":
    return di[injectable.get_fully_qualified_name()]


def clear() -> None:
    di._services = {}
