"""Make sure __version__ matches version in pyproject.toml."""
import re
from pathlib import Path
from aurora_tr import __version__
from loguru import logger


def test_version():
    """Test version."""
    version = ""

    # fetch version in pyproject.toml")
    try:
        text = Path("pyproject.toml").read_text()

        # extract version e.g., 0.1.1a0
        _ = re.findall(r"version\s*=\s*['\"]([\w.]+)", text)
        if _:
            version = _[0]
    except Exception as exc:
        logger.error(exc)

    assert version == __version__
