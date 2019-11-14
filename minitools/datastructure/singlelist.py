__all__ = "SingleList",


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class SingleList:
    __head = None
    __next = None

    class LastObject:
        pass

    def __init__(self, *nodes):
        for node in nodes:
            self.append(node)

    def appendleft(self, value):
        node = Node(value)
        node.next = self.__head
        self.__head = node

    def append(self, value):
        node = Node(value)
        if self.__head is None:
            self.__head = node
        else:
            cur = self.__head
            while cur.next:
                cur = cur.next
            cur.next = node

    def insert(self, index: int, value):
        if index <= 0:
            self.appendleft(value)
        elif index >= self.__len__():
            self.append(value)
        else:
            node = Node(value)
            prior = self.__head
            count = 0
            while count < (index - 1):
                prior = prior.next
                count += 1
            node.next = prior.next
            prior.next = node

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
        self.__exchange(cur, prior)
        return cur.value

    def remove(self, value):
        assert self.__head, "Empty SingleList"
        cur = self.__head
        prior = None
        while cur:
            if value == cur.value:
                return self.__exchange(cur, prior)
            else:
                prior = cur
                cur = cur.next
        raise ValueError("SingleList.remove(x): x not in list")

    def __exchange(self, cur, prior):
        if cur == self.__head:
            self.__head = cur.next
        else:
            prior.next = cur.next

    def reverse(self):
        assert self.__head, "Empty SingleList"
        cur = self.__head
        prior = None
        while cur:
            next = cur.next
            cur.next = prior
            prior = cur
            cur = next
        self.__head = prior

    def index(self, value, index=0):
        assert self.__head, "Empty SingleList"
        assert index < self.__len__(), "list index out of range"
        cur = self.__head
        while index:
            cur = cur.next
            index -= 1
        while cur:
            if value == cur.value:
                return index
            cur = cur.next
            index += 1

    def clear(self):
        del self.__head
        self.__head = None

    def __repr__(self):
        return f"{self.__class__.__name__}{[node for node in self]}"

    def __len__(self, default=0):
        cur = self.__head
        while cur:
            default += 1
            cur = cur.next
        return default

    def __eq__(self, other):
        return [node for node in self] == other

    def __getitem__(self, index: int):
        length = self.__len__()
        assert abs(index) < length, "list index out of range"
        cur = self.__head
        index += length if index < 0 else 0
        while index:
            cur = cur.next
            index -= 1
        return cur.value

    def __setitem__(self, index, value):
        length = self.__len__()
        assert abs(index) < length, "list index out of range"
        cur = self.__head
        index += length if index < 0 else 0
        while index:
            cur = cur.next
            index -= 1
        cur.value = value

    def __iter__(self):
        return self

    def __next__(self):
        if not self.__head:
            raise StopIteration
        cur = self.__next = self.__head if self.__next is None else self.__next
        if cur is self.LastObject:
            self.__next = None
            raise StopIteration
        elif cur.next:
            self.__next = cur.next
            return cur.value
        else:
            self.__next = self.LastObject
            return cur.value

    __str__ = __repr__
    __hash__ = None


if __name__ == '__main__':
    single = SingleList(1, 2, 3, 4, 5, 6)  # SingleList[1, 2, 3, 4, 5, 6]
    single.append(7)  # SingleList[1, 2, 3, 4, 5, 6, 7]
    single.appendleft(0)  # SingleList[0, 1, 2, 3, 4, 5, 6, 7]
    single.insert(2, 1.5)  # SingleList[0, 1, 1.5, 2, 3, 4, 5, 6, 7]
    single.pop()  # SingleList[0, 1, 1.5, 2, 3, 4, 5, 6]
    single.remove(1.5)  # SingleList[0, 1, 2, 3, 4, 5, 6]
    single.reverse()  # SingleList[6, 5, 4, 3, 2, 1, 0]
    single.index(2)  # return 4
    single.clear()  # SingleList[]
    if not single:
        print("This is an empty SingleList")

    single.append(1)
    for i in single:
        print(i)  # return 1

    if (single == [1]):
        print("Test Ok")
