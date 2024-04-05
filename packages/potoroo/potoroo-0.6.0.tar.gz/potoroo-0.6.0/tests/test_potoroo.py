"""Tests for the potoroo package."""

from __future__ import annotations

from eris import ErisResult, Err, Ok

from potoroo import QueryRepo, Repo


class FakeRepo(Repo[int, str]):
    """Fake database."""

    def __init__(self) -> None:
        self._keys = list(range(100))
        self._db: dict[int, str] = {}

    def add(self, some_item: str, /, *, key: int = None) -> ErisResult[int]:
        """Fake add."""
        key = self._keys.pop(0)
        self._db[key] = some_item
        return Ok(key)

    def get(self, key: int) -> ErisResult[str | None]:
        """Fake get."""
        return Ok(self._db[key])

    def remove(self, item: str, /) -> ErisResult[str | None]:
        """Fake remove."""
        item_key = None
        for key, value in self._db.items():
            if value == item:
                item_key = key
                break
        else:
            return Err(f"Unable to find item | {item=}")
        return Ok(self._db.pop(item_key))

    def all(self) -> ErisResult[list[str]]:
        """Fake all."""
        return Ok(sorted(self._db.values()))


class FakeQueryRepo(FakeRepo, QueryRepo[int, str, str]):
    """Fake query repository."""

    def get_by_query(self, query: str) -> ErisResult[list[str]]:
        """Fake get_by_query."""
        return Ok([v for v in self._db.values() if query in v])


def test_repo() -> None:
    """Test the Repo type."""
    repo = FakeRepo()
    foo_idx = repo.add("foo").unwrap()
    baz_idx = repo.add("baz").unwrap()
    assert repo.get(foo_idx).unwrap() == "foo"
    assert repo.update(foo_idx, "bar").unwrap() == "foo"
    assert repo.remove("bar").unwrap() == "bar"
    assert repo.remove_by_key(baz_idx).unwrap() == "baz"


def test_query_repo() -> None:
    """Test the QueryRepo type."""
    repo = FakeQueryRepo()
    foo_idx = repo.add("foo").unwrap()
    repo.add("bar").unwrap()
    repo.add("baz").unwrap()

    assert repo.get(foo_idx).unwrap() == "foo"
    assert repo.get_by_query("f").unwrap() == ["foo"]
    assert repo.all().unwrap() == ["bar", "baz", "foo"]
    assert repo.remove_by_query("b").unwrap() == ["bar", "baz"]
