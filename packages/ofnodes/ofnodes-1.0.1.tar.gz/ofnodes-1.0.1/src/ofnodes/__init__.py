__docformat__ = "restructuredtext"


from ofnodes.nodes.singlynode import SinglyNode
from ofnodes.structures.singlylinkedlist import SinglyLinkedList


__doc__ = """
ofnodes - an illustration of node-based objects and algorithms in Python
========================================================================
**ofnodes** is a Python Package providing examples of the Author's ability
to implement data structures and algorithms in Python. It is not a substitute
for built-in or other third-party implementations of the same data structures
and algorithms. It aims to illustrate the author's ability to produce a
distributable package of objects behind a thoughtful user interface.

Main Features
-------------
Here is what ofnodes can do:
    - implement a node object with a unidirectional pointer
    - implement and manipulate a linked list object of unidirectional,
    i.e., 'singly linked' nodes.
"""
__all__ = ['SinglyNode','SinglyLinkedList']