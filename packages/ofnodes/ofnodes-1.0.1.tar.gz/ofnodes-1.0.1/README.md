# ofnodes

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-%3E=3.11.5-blue.svg)](https://www.python.org/downloads/release/python-3115/)

**ofnodes** is a Python Package providing examples of the Author's ability
to implement data structures and algorithms in Python. It is not a substitute
for built-in or other third-party implementations of the same data structures
and algorithms. It aims to illustrate the author's ability to produce a
distributable package of objects behind a thoughtful user interface.

## Features
Here is what ofnodes can do:
    - implement a node object with a unidirectional pointer
    - implement and manipulate a linked list object of unidirectional,
    i.e., 'singly linked' nodes.

## Installation
```python
pip install ofnodes
```

## Usage


```python
# what's a better markdown fenced code block for repl?
>>> llist = SinglyLinkedList()
>>> llist.head = "first node"
>>> llist.head = [42.0, True, "LGRW"]
>>> llist.tail = "third node added to list"
>>> llist
SinglyLinkedList(head=This node's data is 3 of type list., tail=This node's data is 24 of type str.)
>>> llist.tail = None
>>> llist
SinglyLinkedList(head=This node's data is 3 of type list., tail=This node's data is of type NoneType.)
>>> llist.head.next.data
'first node'
>>> llist.remove_tail()
>>> llist.tail.data
'third node added to list'
```
For more usage examples, please refer to the [Documentation][1]

## Documentation
For detailed usage information , API reference, and code examples,
please refer to the [Documentation][1].


[1]: https://robert-portelli.github.io/ofnodes/