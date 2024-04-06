# pylint: disable=missing-function-docstring, missing-class-docstring, missing-module-docstring

import pytest

from fixpoint_sdk.types import ModeType, parse_mode_type


def test_parse_mode_type() -> None:
    """Test parse_mode_type."""
    assert parse_mode_type() == ModeType.MODE_UNSPECIFIED
    assert parse_mode_type(None) == ModeType.MODE_UNSPECIFIED
    assert parse_mode_type("unspecified") == ModeType.MODE_UNSPECIFIED
    assert parse_mode_type("test") == ModeType.MODE_TEST
    assert parse_mode_type("staging") == ModeType.MODE_STAGING
    assert parse_mode_type("prod") == ModeType.MODE_PROD
    assert parse_mode_type(0) == ModeType.MODE_UNSPECIFIED
    assert parse_mode_type(1) == ModeType.MODE_TEST
    assert parse_mode_type(2) == ModeType.MODE_STAGING
    assert parse_mode_type(3) == ModeType.MODE_PROD

    for bad_val in ["", "unknown", 4, -1, 1.0, object()]:
        with pytest.raises(ValueError):
            parse_mode_type(bad_val)
