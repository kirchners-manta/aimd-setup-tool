"""
Setup for pytest.
"""

import numpy as np
import pytest

np.random.seed(0)
np.set_printoptions(precision=16)


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the ``--update-golden`` option to pytest.

    Parameters
    ----------
    parser : pytest.Parser
        The pytest command line parser.
    """
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Regenerate the reference files in test/data/golden "
        "instead of comparing against them.",
    )


@pytest.fixture
def update_golden(request: pytest.FixtureRequest) -> bool:
    """Whether the golden reference files should be regenerated.

    Parameters
    ----------
    request : pytest.FixtureRequest
        The pytest request object.

    Returns
    -------
    bool
        True if pytest was called with ``--update-golden``.
    """
    return bool(request.config.getoption("--update-golden"))
