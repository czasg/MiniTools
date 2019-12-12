from scrapy.squeues import PickleLifoDiskQueue

__all__ = "",
test_path = "minitools.scrapy.squeues.SafePickleLifoDiskQueue"


class SafePickleLifoDiskQueue(PickleLifoDiskQueue):

    # def __init__(self, path):
    #     super(SafePickleLifoDiskQueue, self).__init__(path)

    def open(self):
        super(SafePickleLifoDiskQueue, self).__init__(self.path)

    def push(self, obj):
        self.open()
        super(SafePickleLifoDiskQueue, self).push(obj)
        self.close()

    def pop(self):
        self.open()
        data = super(SafePickleLifoDiskQueue, self).pop()
        return data
