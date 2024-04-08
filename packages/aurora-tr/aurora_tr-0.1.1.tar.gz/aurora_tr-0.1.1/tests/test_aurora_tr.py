"""
Test aurora_tr.

run `rye run pytest`
"""
import pytest
import stamina
from aurora_tr import aurora_tr


@pytest.fixture(autouse=True, scope="session")
def deactivate_retries():
    stamina.set_active(False)


def test_aurora_tr_empty_input():
    """Test aurora_tr empty input."""
    _ = aurora_tr("  ")
    assert _.get("translation").startswith(" ")


def test_aurora_tr_url():
    """Test aurora_tr url."""
    _ = aurora_tr("https://www.baidu.com")
    assert _.get("translation").startswith("http")


def test_aurora_tr_dw_text():
    """Test aurora_tr digital twin text."""
    text = "A digital twin is a virtual model or representation of an object, component, or system that can be updated through real-time data via sensors, either within the object itself or incorporated into the manufacturing process."
    _ = aurora_tr(text)

    _ = _.get("translation")
    assert "数字" in _ or "实时" in _ or "更新" in _
