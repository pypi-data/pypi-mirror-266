"""Utilities for setting up or parsing the configuration environment."""

import os
import typing

from .exc import InitException
from .logging import logger

BASE_URL = "https://api.fixpoint.co"

_FIXPOINT_BASE_URL_ENV_KEY = "FIXPOINT_API_BASE_URL"


def get_fixpoint_api_key(api_key: typing.Optional[str]) -> str:
    """Returns the Fixpoint API key from the environment or the argument.

    Returns the Fixpoint API key from the environment or the argument,
    preferring the argument. If no key is defined, we raise an exception.
    """
    if api_key:
        return api_key

    if "FIXPOINT_API_KEY" not in os.environ:
        logger.error("FIXPOINT_API_KEY env variable not set.")
        raise InitException("Fixpoint API key not set")

    key = os.environ["FIXPOINT_API_KEY"]
    if not key:
        logger.error("FIXPOINT_API_KEY env variable is empty.")
        raise InitException("Fixpoint API key is empty")
    return key


def get_api_base_url(base_url: typing.Optional[str]) -> str:
    """Returns the API base URL for Fixpoint. If not set, returns the default."""
    burl = _get_api_base_url(base_url)
    if burl[-1] == "/":
        return burl[:-1]
    return burl


def _get_api_base_url(base_url: typing.Optional[str]) -> str:
    if base_url:
        return base_url
    if _FIXPOINT_BASE_URL_ENV_KEY in os.environ:
        base_url = os.environ[_FIXPOINT_BASE_URL_ENV_KEY]
        if not base_url:
            logger.error("%s env variable is empty.", _FIXPOINT_BASE_URL_ENV_KEY)
            raise InitException("Fixpoint API base URL is empty")
        return base_url
    return BASE_URL
