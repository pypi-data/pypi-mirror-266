"""Defines a node for a singly linked list.

This module contains the definition for the `SinglyNode` class, which represents
a node in a singly linked list. Each node contains data and a reference to the
next node in the list.

Example:
    Typical usage example:

        uni_node = SinglyNode("a string of characters")
"""

from typing import Any, Optional

#from ofnodes.nodes.node import Node

class SinglyNode:
    """Represents a node in a singly linked list.

    Attributes:
        data: The data stored in the node.
        next: Reference to the next node in the linked list. Defaults to None.
    """

    def __init__(self, data: Any) -> None:
        self._data: Optional[Any] = data
        self._next: Optional[SinglyNode] = None

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        # all data welcome
        self._data = value

    @property
    def next(self):
        return self._next

    @next.setter
    def next(self, value):
        raise AttributeError("Cannot set 'next' attribute directly. Use linked list methods for modification.")

    def __repr__(self) -> str:
        # when repr is called on a Node with .next,
        # is next=itsvalue in the return?
        return (
            f"{type(self).__name__}("
            f"data={repr(self.data)}"
            #f", next={repr(self.next)}"
            ")"
        )

    def __str__(self) -> str:
        if hasattr(self.data, "__len__"):
            return (
                "This node's data is"
                f" {len(self.data)}"  # type: ignore # noqa
                f" of type {type(self.data).__name__}."
            )
        return f"This node's data is of type {type(self.data).__name__}."
