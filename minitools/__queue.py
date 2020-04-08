from queue import Queue, PriorityQueue
from collections import defaultdict
from typing import Any

class User:
    def __init__(self, sock):
        self.sock = sock
    def setMQ(self, mq):
        self.mq = mq
    def put(self, item):
        raise NotImplementedError
    def notify(self):
        raise NotImplementedError

class MiniMQ:
    topic_pool = defaultdict(Queue)
    observers = defaultdict(list)

    def addSubscriber(self, topic: str, subscriber: User) -> None:
        if topic in self.topic_pool:
            self.observers[topic].append(subscriber)

    def removeSubscriber(self, topic: str, subscriber: User) -> None:
        if topic in self.observers:
            self.observers[topic].remove(subscriber)

    def notifySubscriber(self, topic: str) -> None:
        for subscriber in self.observers.get(topic, []):
            subscriber.notify()

    def put(self, topic: str, item: Any) -> None:
        self.topic_pool[topic].put_nowait(item)
        self.notifySubscriber(topic)


class Publisher(User):
    topic_s = []
    mq: MiniMQ = None

    def put(self, item):
        for topic in self.topic_s:
            self.mq.put(topic, item)


class Subscriber(User):
    topic_s = []
    mq: MiniMQ = None

    def notify(self):
        "本质是通知订阅方，"


import socket
# import asyncio
import threading
from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
# loop = asyncio.get_event_loop()
mq = MiniMQ()
selector = DefaultSelector()
users = []
sock = socket.socket()
sock.bind(("localhost", 8888))
sock.listen(10)
def sub_conn(fileobj):
    for user in users:
        if user.sock.fileno() == fileobj:
            print("找到了Sub1111")
            soc, a = user.sock.accept()
            subscriber = Subscriber(soc)
            subscriber.setMQ(mq)
            selector.register(soc.fileno(), EVENT_READ, sub_read)
            users.append(subscriber)
selector.register(sock.fileno(), EVENT_READ, sub_conn)
class Temp:
    sock = None
temp = Temp()
temp.sock = sock
users.append(temp)
def sub_read(fileobj):
    for user in users:
        if user.sock.fileno() == fileobj:
            data = user.sock.recv(1024)
            if data == b'':
                print("断开连接")
                selector.unregister(fileobj)
                return
            print(f"找到了Sub: {data}")

def pub_conn(fileobj):
    for user in users:
        if user.sock.fileno() == fileobj:
            soc, address = user.sock.accept()
            publisher = Publisher(soc)
            publisher.setMQ(mq)
            selector.register(soc.fileno(), EVENT_READ, pub_read)
            users.append(publisher)
            print("注册一位Pub")
sock1 = socket.socket()
sock1.bind(("localhost", 8889))
sock1.listen(10)
selector.register(sock1.fileno(), EVENT_READ, pub_conn)
class Temp1:
    sock = None
temp1 = Temp1()
temp1.sock = sock1
users.append(temp1)
def pub_read(fileobj):
    for user in users:
        if user.sock.fileno() == fileobj:
            pass

def loop():
    while True:
        events = selector.select()
        print(events)
        for selectorKey, mask in events:
            callback_func = selectorKey.data
            callback_func(selectorKey.fd)

if __name__ == '__main__':
    # threading.Thread(target=subscriber).start()
    # threading.Thread(target=publisher).start()
    # loop.run_forever()
    loop()


