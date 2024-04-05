"""The `*Repo` abstract types which implement the "Repository" pattern."""

from __future__ import annotations

import abc
from typing import Generic, Optional, TypeVar

from eris import ErisResult, Err, Ok


K = TypeVar("K")
V = TypeVar("V")
Q = TypeVar("Q")


class BasicRepo(Generic[K, V], abc.ABC):
    """The simplest possible Repository type."""

    @abc.abstractmethod
    def add(self, item: V, /, *, key: K = None) -> ErisResult[K]:
        """Add a new `item` to the repo and associsate it with `key`."""

    @abc.abstractmethod
    def get(self, key: K) -> ErisResult[Optional[V]]:
        """Retrieve an item from the repo by key."""


class Repo(BasicRepo[K, V], Generic[K, V], abc.ABC):
    """A full-featured Repository

    Adds the ability to update, delete, and list all items ontop of the
    BasicRepo type.
    """

    @abc.abstractmethod
    def remove(self, item: V, /) -> ErisResult[Optional[V]]:
        """Remove an item from the repo."""

    def remove_by_key(self, key: K) -> ErisResult[Optional[V]]:
        """Remove an item from the repo by key."""
        item_result = self.get(key)
        if isinstance(item_result, Err):
            err: Err = Err(
                "An error occurred while fetching the item to be removed."
            ).chain(item_result)
            return err

        item = item_result.ok()
        assert item is not None
        return self.remove(item)

    def update(self, key: K, item: V, /) -> ErisResult[V]:
        """Update an item by key."""
        old_item_result = self.remove_by_key(key)
        if isinstance(old_item_result, Err):
            err: Err = Err(
                "An error occurred while removing the old item."
            ).chain(old_item_result)
            return err

        old_item = old_item_result.ok()
        if old_item is None:
            return Err(f"Old item with this ID does not exist. | id={key}")

        self.add(item, key=key).unwrap()

        return Ok(old_item)

    @abc.abstractmethod
    def all(self) -> ErisResult[list[V]]:
        """Retrieve all items stored in this repo."""


class QueryRepo(Repo[K, V], Generic[K, V, Q], abc.ABC):
    """A Repository that is aware of some kind of "querys".

    Adds the ability to retrieve / delete a group of objects based off of some
    arbitrary "query" type.

    NOTE: In general, K can be expected to be a primitive type, whereas Q is
      often a custom user-defined type.
    """

    @abc.abstractmethod
    def get_by_query(self, query: Q) -> ErisResult[list[V]]:
        """Retrieve a group of items that meet the given query's criteria."""

    def remove_by_query(self, query: Q) -> ErisResult[list[V]]:
        """Remove a group of items that meet the given query's criteria."""
        items_result = self.get_by_query(query)
        err: Optional[Err] = None
        if isinstance(items_result, Err):
            err = Err(
                "An error occurred while fetching items to be removed by"
                " query."
            ).chain(items_result)
            return err

        deleted_items: list[V] = []
        items = items_result.ok()
        for item in items:
            deleted_item_result = self.remove(item)
            other_items = set(items) - set(deleted_items)
            if isinstance(deleted_item_result, Err):
                err = Err(
                    "An error occurred while removing item |"
                    f" {item=} {deleted_items=} {other_items=}"
                )
                return err
            deleted_item = deleted_item_result.ok()
            assert deleted_item is not None
            deleted_items.append(deleted_item)

        return Ok(deleted_items)
