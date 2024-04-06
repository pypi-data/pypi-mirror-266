import pytest

from antimatter.dependencies.versions import as_install_hint, _parse_requirements
from antimatter.errors.errors import MissingDependency


def test_as_install_hint():
    # For this to pass, the requirements will need to be findable and parseable
    hint = as_install_hint("pandas")
    assert "pip install pandas" in hint
