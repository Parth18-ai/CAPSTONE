import pytest
from app.agent.tools import unit_convert


def test_nm_to_lbf_ft():
    assert unit_convert(108, "Nm", "lbf-ft") == 79.66


def test_unsupported():
    with pytest.raises(ValueError):
        unit_convert(1, "nm", "bar")
