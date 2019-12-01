from weakref import ref, finalize
from contextlib import contextmanager
from threading import RLock, current_thread

__all__ = 'minilocal',


class _MiniLocal:
    key = None
    dicts = dict()

    def __init__(self):
        self.key = f"_minilocal.{id(self)}"

    @classmethod
    def get_thread_dict(cls):
        thread = current_thread()  # can't as arguments, because it will be fixed by main thread
        thread_tuple = cls.dicts.get(id(thread), None)
        return thread_tuple[1] if thread_tuple else None

    @classmethod
    def create_thread_dict(cls):
        new_dict = dict()
        key = cls.key
        thread = current_thread()
        thread_id = id(thread)

        def weak_local_callback(key=key):
            thread = weak_thread()
            if thread is not None:
                thread.__dict__.pop(key, None)

        def weak_thread_callback(thread_id=thread_id):
            local = weak_local()
            if local is not None:
                local.dicts.pop(thread_id, None)

        weak_local = ref(cls)
        finalize(cls, weak_local_callback)
        weak_thread = ref(thread)
        finalize(thread, weak_thread_callback)

        thread.__dict__[key] = weak_local
        cls.dicts[thread_id] = weak_thread, new_dict
        return new_dict


get_thread_dict = _MiniLocal.get_thread_dict
create_thread_dict = _MiniLocal.create_thread_dict


@contextmanager
def wrapper_lock(local):
    local_dict = get_thread_dict()
    if local_dict is None:
        local_dict = create_thread_dict()
    with RLock():
        object.__setattr__(local, '__dict__', local_dict)
        yield


class MiniLocal:
    __slots__ = "_minilocal__instance", "__dict__"

    def __new__(cls, *args, **kwargs):
        assert not args and not kwargs, "Not support Arguments"
        _local = object.__new__(cls)
        _minilocal = _MiniLocal()
        object.__setattr__(_local, '_minilocal__instance', _minilocal)  # can't use setattr
        create_thread_dict()
        return _local

    def __getattribute__(self, item):
        with wrapper_lock(self):
            return object.__getattribute__(self, item)

    def __setattr__(self, key, value):
        assert key != '__dict__', "attribute '__dict__' is read-only"
        with wrapper_lock(self):
            return object.__setattr__(self, key, value)

    def __delattr__(self, item):
        assert item != '__dict__', "attribute '__dict__' is read-only"
        with wrapper_lock(self):
            return object.__delattr__(self, item)


minilocal = MiniLocal
