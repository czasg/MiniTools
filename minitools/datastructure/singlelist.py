__all__ = "SingleList",

"""
is_empty() 链表是否为空
length() 链表长度
travel() 遍历整个链表
add(item) 链表头部添加元素
append(item) 链表尾部添加元素
insert(pos, item) 指定位置添加元素
remove(item) 删除节点
search(item) 查找节点是否存在

"""


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


class SingleList:
    __head = None

    def __init__(self, *nodes):
        for node in nodes:
            self.append(node)

    def is_empty(self):
        return self.__head == None

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

    def remove(self, value):
        assert self.__head, "Empty SingleList"
        cur = self.__head
        prior = None
        while cur:
            if value == cur.value:
                if cur == self.__head:
                    self.__head = cur.next
                else:
                    prior.next = cur.next
                return
            else:
                prior = cur
                cur = cur.next
        raise ValueError("SingleList.remove(x): x not in list")

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

    def traverse(self):
        cur = self.__head
        while cur:
            print(cur.value)
            cur = cur.next

    def __len__(self, default=0):
        cur = self.__head
        while cur:
            default += 1
            cur = cur.next
        return default

    # def __getitem__(self, item):
    #     return item

    def __iter__(self):
        return self

    def __next__(self):
        temp = getattr(self, 'temp', None)
        cur = self.__head
        while cur:
            yield cur.value
            cur = cur.next
        # return self

    __hash__ = None


if __name__ == '__main__':
    test = SingleList(1, 2, 3, 4, 5, 6)

    # for i, j in enumerate(test):
    #     if i == 10:
    #         break
    #     print(j)



