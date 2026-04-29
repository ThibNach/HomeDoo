import pytest
from modules.registry import Registry


def test_sort_simple_dependency():
    manifests = {
        "a": {"name": "A", "dependencies": ["b"]},
        "b": {"name": "B", "dependencies": []}
    }

    result = Registry().sort_by_dependencies(manifests)

    assert result.index("b") < result.index("a")


def test_sort_no_dependencies():
    manifests = {
        "a": {"name": "A", "dependencies": []},
        "b": {"name": "B", "dependencies": []},
        "c": {"name": "C", "dependencies": []}
    }

    result = Registry().sort_by_dependencies(manifests)

    assert set(result) == {"a", "b", "c"}
    assert len(result) == 3


def test_sort_chain_dependencies():
    manifests = {
        "c": {"name": "C", "dependencies": ["b"]},
        "b": {"name": "B", "dependencies": ["a"]},
        "a": {"name": "A", "dependencies": []}
    }

    result = Registry().sort_by_dependencies(manifests)

    assert result.index("a") < result.index("b") < result.index("c")


def test_sort_multiple_dependencies():
    manifests = {
        "c": {"name": "C", "dependencies": ["a", "b"]},
        "a": {"name": "A", "dependencies": []},
        "b": {"name": "B", "dependencies": []}
    }

    result = Registry().sort_by_dependencies(manifests)

    assert result.index("a") < result.index("c")
    assert result.index("b") < result.index("c")


def test_sort_circular_dependency_raises():
    manifests = {
        "a": {"name": "A", "dependencies": ["b"]},
        "b": {"name": "B", "dependencies": ["a"]}
    }

    with pytest.raises(ValueError, match="Circular dependencies"):
        Registry().sort_by_dependencies(manifests)


def test_sort_handles_uppercase_names():
    manifests = {
        "auth": {"name": "Auth", "dependencies": []},
        "calendar": {"name": "Calendar", "dependencies": ["Auth"]}
    }

    result = Registry().sort_by_dependencies(manifests)

    assert result.index("auth") < result.index("calendar")