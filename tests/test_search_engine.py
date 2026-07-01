import pytest

from sciseek.core.exceptions import ValidationError
from sciseek.core.models import SearchMode
from sciseek.searchers.engine import SearchEngine


def test_simple_case_sensitive():
    eng = SearchEngine(case_sensitive=True)
    out = eng.search(SearchMode.SIMPLE, "ABC abc", ["ABC"])
    assert out.match_count == 1


def test_regex_invalid_raises():
    eng = SearchEngine()
    with pytest.raises(ValidationError):
        eng.validate_regex_terms(["("])


def test_proximity_requires_two_terms():
    eng = SearchEngine()
    with pytest.raises(ValidationError):
        eng.search(SearchMode.PROXIMITY, "alpha beta", ["alpha"])
