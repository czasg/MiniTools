__all__ = 'tlist',


class Node:
    def __init__(self, value):
        self.prev = None
        self.next = None
        self.value = value


class TwoWayLinkedList:
    __head = None

    @property
    def head(self):
        return self.__head

    def __init__(self, *nodes):
        for node in nodes:
            self.append(node)

    def appendleft(self, value):
        node = Node(value)
        if not self.__head:
            self.__head = node
        else:
            node.next = self.__head
            self.__head.prev = node
            self.__head = node

    def append(self, value):
        node = Node(value)
        cur = self.__head
        if not cur:
            self.__head = Node
            return
        while cur.next:
            cur = cur.next
        cur.next = node
        node.prev = cur

    def insert(self, index, value):
        if index <= 0:
            self.appendleft(value)
        elif index >= self.__len__():
            self.append(value)
        else:
            node = Node(value)
            cur = self.__head
            index = index - 1
            while index:
                cur = cur.next
                index -= 1
            node.next = cur.next
            cur.next.prev = node
            node.prev = cur
            cur.next = node

    def extend(self, dataSet):
        tList = self.__buildSingleList(dataSet)
        if not self.__head:
            self.__head = tList.head
            return
        cur = self.__head
        while cur.next:
            cur = cur.next
        cur.next = tList.head
        tList.head.prev = cur

    def __buildSingleList(self, dataSet):
        tList = dataSet
        if not isinstance(tList, TwoWayLinkedList):
            tList = TwoWayLinkedList(*dataSet)
        return tList

    def pop(self, index=-1):
        length = self.__len__()
        assert abs(index) < length, "list index out of range"
        cur = self.__head
        prior = None
        index += length if index < 0 else 0
        while index:
            prior = cur
            cur = cur.next
            index -= 1
        self.__exchange(cur, prior)  # todo
        return cur.value

    def __len__(self, default=0):
        cur = self.__head
        while cur:
            default += 1
            cur = cur.next
        return default


tlist = TwoWayLinkedList
