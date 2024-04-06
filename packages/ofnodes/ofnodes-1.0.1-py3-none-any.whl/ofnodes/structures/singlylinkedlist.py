from typing import Optional, Any

from ofnodes.nodes.singlynode import SinglyNode


class SinglyLinkedList:
    """A class representing a singly linked list.

    This class provides functionality to create and manipulate a singly linked list
    data structure. Each node in the linked list contains a reference to the next
    node in the sequence.

    Attributes:
        _head (Optional[SinglyNode]): The head of the linked list.
        _tail (Optional[SinglyNode]): The tail of the linked list.

    Examples:
        >>> linked_list = SinglyLinkedList()
        >>> linked_list
        SinglyLinkedList(head=None, tail=None)
    """
    def __init__(self) -> None:
        self._head: Optional[SinglyNode] = None
        self._tail: Optional[SinglyNode] = None

    @property
    def head(self) -> SinglyNode | None:
        """Getter property for the head of the linked list.

        Returns:
            SinglyNode | None: The head of the linked list, or None if the list is empty.

        Notes:
            The `head` property allows access to the first node in the linked list.

        Examples:
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
        """
        return self._head

    @head.setter
    def head(self, value: SinglyNode | Any) -> None:
        """
        Setter property for the head of the linked list.

        Args:
            value (SinglyNode | Any): The value to be set as the head. If the value is
                not already a SinglyNode object, it is wrapped in a SinglyNode.

        Raises:
            AttributeError: If attempting to delete the `head` attribute.
        """
        match value:
            case SinglyNode():
                node = value
            case _:
                node = SinglyNode(value)

        match self._head:
            case None:
                self._head = node
                self._tail = node

            case self._head:
                setattr(node, '_next', self._head)
                setattr(self, "_head", node)

    @head.deleter
    def head(self):
        """Deleter property for the head of the linked list.

        Raises:
            AttributeError: Deleting the `head` attribute is not allowed.
        """
        raise AttributeError(
            f"{type(self).__name__}'s `head` attribute " "cannot be deleted."
        )

    @property
    def tail(self) -> SinglyNode | None:
        """
        Getter property for the tail of the linked list.

        Returns:
            SinglyNode | None: The tail of the linked list, or None if the list is empty.

        Examples:
            >>> llist = SinglyLinkedList()
            >>> llist
            SinglyLinkedList(head=None, tail=None)
            >>> llist.tail = "first node in the list"
            >>> assert llist.tail is llist.head
            >>> assert llist.next is None
            >>> assert llist.head.next is None
            >>> llist.tail
            >>> llist.tail = "new tail"
            >>> assert llist.head.next is llist.tail
            >>> llist
            SinglyLinkedList(head=This node's data is 22 of type str., tail=This node's data is 8 of type str.)
            >>> llist.__dict__
            {'_head': SinglyNode(data='first node in the list'), '_tail': SinglyNode(data='new tail')}
            >>> llist.head, llist.tail
            (SinglyNode(data='first node in the list'), SinglyNode(data='new tail'))
        """
        return self._tail

    @tail.setter
    def tail(self, value: SinglyNode | Any) -> None:
        """Setter property for the tail of the linked list.

        Args:
            value (SinglyNode | Any): The value to be set as the tail. If the value is
                not already a SinglyNode object, it is wrapped in a SinglyNode.

        Notes:
            Setting the `tail` property allows modification of the last node in the linked list.
        """
        match value:
            case SinglyNode():
                node = value
            case _:
                node = SinglyNode(value)

        match self._head:
            case None:
                setattr(self, "_head", node)
                setattr(self, "_tail", node)
            case self._head:
                if not getattr(self._head, "_next"):
                    # it's a one node list
                    setattr(self._head, "_next", node)
                    setattr(self, "_tail", node)
                    return
                # there're more than one node
                setattr(self._tail, "_next", node)
                setattr(self, "_tail", node)

    @tail.deleter
    def tail(self):
        """Deleter property for the tail of the linked list.

        Raises:
            AttributeError: Deleting the `tail` attribute is not allowed.
        """
        raise AttributeError(
            f"{type(self).__name__}'s `tail` attribute " "cannot be deleted."
        )

    def __repr__(self) -> str:
        return f"{type(self).__name__}(head={self.head}, tail={self.tail})"

    def __str__(self) -> str:
        match self:
            case SinglyLinkedList(head=None, tail=None):
                return "This instance of SinglyLinkedList is empty."
            case SinglyLinkedList(head=head, tail=tail):
                if head is tail:
                    return "This instance of SinglyLinkedList has a single node."
                return "The head and tail are different nodes."

    def insert_head(self, data: Any) -> None:
        """ Inserts a new node with the provided data at the head of the linked list.

        Args:
            data: The data to be inserted into the new node. If the data is already a
                `SinglyNode` object, it is inserted directly; otherwise, a new
                `SinglyNode` object is created with the provided data.

        Returns:
            None

        Notes:
            If the linked list is empty, the new node becomes both the head and the
            tail of the linked list. If the linked list is not empty, the new node
            is inserted at the beginning of the list by updating the `next` attribute
            of the new node to point to the current head node, and then updating the
            instance's `head` attribute to reference the new node.

        Examples:
            >>> linked_list = SinglyLinkedList()
            >>> linked_list
            SinglyLinkedList(head=None, tail=None)
            >>> linked_list.insert_head("the first node in the list")
            >>> assert linked_list.head is linked_list.tail
            >>> linked_list.insert_head({"the second node": (42.0, True, SinglyNode("LGRW"))})
            >>> assert (
            ...     linked_list.head is not linked_list.tail
            ...     and
            ...     linked_list.head.next is linked_list.tail
            ... )
            >>> linked_list.head, linked_list.tail
            (SinglyNode(data={'the second node': (42.0, True, SinglyNode(data='LGRW'))}), SinglyNode(data='the first node in the list'))
            >>> linked_list.head = "third node added as head via property"
            >>> linked_list.head, linked_list.tail
            (SinglyNode(data='third node added as head via property'), SinglyNode(data='the first node in the list'))
            >>> linked_list.head.__dict__
            {'_data': 'third node added as head via property', '_next': SinglyNode(data={'the second node': (42.0, True, SinglyNode(data='LGRW'))})}
            >>> llist = SinglyLinkedList()
            >>> list(llist.insert_head(f"{i} node") for i in range(1, 5))
            [None, None, None, None]
            >>> llist.head = "to be assigned to `SinglyNode.data` then `SinglyLinkedList.head`"
            >>> llist.head, llist.head.next, llist.tail
            (SinglyNode(data='to be assigned to `SinglyNode.data` then `SinglyLinkedList.head`'), SinglyNode(data='4 node'), SinglyNode(data='1 node'))
        """
        self.head = data  # trigger the head setter

    def insert_tail(self, data: Any) -> None:
        """Inserts a new node with the provided data at the tail of the linked list.

        Args:
            data: The data to be inserted into the new node. If the data is already a
                `SinglyNode` object, it is inserted directly; otherwise, a new
                `SinglyNode` object is created with the provided data.

        Returns:
            None

        Notes:
            If the linked list is empty, the new node becomes both the head and the
            tail of the linked list. Otherwise, the new node is appended to the end
            of the list by updating the `next` attribute of the current tail node
            to point to the new node, and then updating the instance's `tail`
            attribute to reference the new node.

        Examples:
            >>> linked_list = SinglyLinkedList()
            >>> linked_list
            SinglyLinkedList(head=None, tail=None)
            >>> linked_list.insert_tail("the first node in a list")
            >>> assert linked_list.head is linked_list.tail
            >>> linked_list.head, linked_list.head.next, linked_list.tail
            (SinglyNode(data='the first node in a list'), None, SinglyNode(data='the first node in a list'))
            >>> linked_list.insert_tail({"the second node": (42.0, True, SinglyNode("LGRW"))})
            >>> linked_list.head, linked_list.head.next, linked_list.tail
            (SinglyNode(data='the first node in a list'), SinglyNode(data={'the second node': (42.0, True, SinglyNode(data='LGRW'))}), SinglyNode(data={'the second node': (42.0, True, SinglyNode(data='LGRW'))}))
            >>> assert linked_list.head is not linked_list.tail
            >>> assert linked_list.head.next is linked_list.tail
            >>> linked_list.tail
            SinglyNode(data={'the second node': (42.0, True, SinglyNode(data='LGRW'))})
            >>> linked_list.tail.data['the second node']
            (42.0, True, SinglyNode(data='LGRW'))
            >>> linked_list.tail.data['the second node'][2].data
            'LGRW'
            >>> linked_list.tail = "insert 3rd node via property"
            >>> linked_list.tail.__dict__
            {'_data': 'insert 3rd node via property', '_next': None}
            >>> linked_list.tail.data
            'insert 3rd node via property'
            >>> llist = SinglyLinkedList()
            >>> list(llist.insert_tail(f"{i} node") for i in range(1, 5))
            >>> llist.head, llist.head.next, llist.tail
            (SinglyNode(data='1 node'), SinglyNode(data='2 node'), SinglyNode(data='4 node'))
            >>> llist.tail = "is passed to setter to become SinglyNode()"
            >>> llist.head, llist.head.next, llist.tail
            (SinglyNode(data='1 node'), SinglyNode(data='2 node'), SinglyNode(data='is passed to setter to become SinglyNode()'))
        """
        self.tail = data  # trigger the tail setter

    def search(self, target) -> bool:
        """Searches for a target value in the linked list.

        Args:
            target (Any): The value to search for in the linked list.

        Returns:
            bool: True if the target value is found in the linked list, False otherwise.

        Raises:
            ValueError: If the linked list is empty.

        Notes:
            This method iterates through the linked list starting from the head node
            and checks each node's data value for equality with the target value.

        Examples:
            >>> llist = SinglyLinkedList()
            >>> llist.head = "first node"
            >>> llist.head = "second node"
            >>> llist.search("first node")
            True
            >>> llist.search(SinglyNode("first node"))
            False
            >>> llist.search("third node")
            False
            >>> llist.tail = "third node"
            >>> llist.search("third node")
            True
        """
        if self._head:
            current_node = self._head
            while current_node:
                if current_node.data == target:
                    return True
                current_node = current_node.next
            return False
        raise ValueError("Cannot perform search: The list is empty.")

    def remove_head(self) -> None:
        """Removes the head node from the linked list.

        Raises:
            ValueError: If the linked list is empty.

        Returns:
            None

        Notes:
            - If the head node is the only node in the list, both the head and tail references are set to None.
            - If the head node is not the only node, the head reference is updated to point to the next node.
            TODO: overload `-` operator to support:
                    1) `linked_list - linked_list.head`
                    2) `linked_list - linked_list.tail`
                    3) `linked_list - linked_list.spot()`

        Examples:
            >>> sllist = SinglyLinkedList()
            >>> sllist
            SinglyLinkedList(head=None, tail=None)
            >>> sllist.head = {42: "a string"}
            >>> sllist
            SinglyLinkedList(head=This node's data is 1 of type dict., tail=This node's data is 1 of type dict.)
            >>> sllist.head.data[42]
            'a string'
            >>> sllist.remove_head()
            >>> sllist
            SinglyLinkedList(head=None, tail=None)
        """
        if self._head and self._head is self._tail:
            self._head = None
            self._tail = None
            return
        if self._head and self._head is not self._tail:
            self._head = self.head.next
            return
        raise ValueError("Cannot remove head from empty list")

    def remove_tail(self) -> None:
        """Removes the tail node from the linked list.

        Raises:
            ValueError: If the linked list is empty.

        Returns:
            None

        Examples:
            >>> linked_list = SinglyLinkedList()
            >>> linked_list
            SinglyLinkedList(head=None, tail=None)
            >>> linked_list.head = True
            >>> linked_list
            SinglyLinkedList(head=This node's data is of type bool., tail=This node's data is of type bool.)
            >>> linked_list.tail = ['strings', SinglyNode(lambda x: str(x)*2)]
            >>> linked_list
            SinglyLinkedList(head=This node's data is of type bool., tail=This node's data is 2 of type list.)
            >>> linked_list.tail
            SinglyNode(data=['strings', SinglyNode(data=<function <lambda> at 0x74a9932a2fc0>)])
            >>> linked_list.tail.data[1].data
            <function <lambda> at 0x74a9932a2fc0>
            >>> x = linked_list.tail.data[1].data
            >>> x("skrrt")
            'skrrtskrrt'
            >>> linked_list.remove_tail()
            >>> x("skrrt")
            'skrrtskrrt'
            >>> linked_list.tail
            SinglyNode(data=True)
            """
        match self._head:
            case None:
                raise ValueError("Cannot remove tail from empty list")
            case self._head:
                if not getattr(self._head, "_next"):
                    # it's a one node list
                    setattr(self, "_head", None)
                    setattr(self, "_tail", None)
                    return
                if getattr(self._head, "next") is self._tail:
                    # there are two nodes
                    setattr(self, "_tail", self._head)
                    setattr(self._tail, "_next", None)
                    return
                # there are more than two nodes
                node = self._head
                # find second to last node
                while getattr(node, "_next") and getattr(node._next, "_next"):
                    if getattr(node._next, "_next") is self._tail:
                        node = getattr(node, "_next")  # target found
                        break
                    node = getattr(node, "_next")  # keep looking
                setattr(node, "_next", None)  # point the second to last node to None
                setattr(self, "_tail", node)  # assign tail to the node

    def print_node_data(self) -> None:
        """Traverse the linked list and print the data attribute of each node.

        Returns:
            None

        Notes:
            This method iterates through the linked list starting from the head node and prints the data attribute of each node
            until the end of the list is reached.

        Examples:
            >>> sllist = SinglyLinkedList()
            >>> list(sllist.insert_tail(f"{i} node") for i in range(1, 5))
            [None, None, None, None]
            >>> sllist.head
            SinglyNode(data='1 node')
            >>> sllist.tail
            SinglyNode(data='4 node')
            >>> sllist.print_node_data()
            1 node
            2 node
            3 node
            4 node
        """
        current_node = self._head
        while current_node:
            print(current_node.data)
            current_node = current_node.next
