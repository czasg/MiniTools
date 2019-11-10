import threading

__all__ = ('timeout', 'get_lock', 'get_condition', 'get_local')


def timeout(func=None, timeout=20):
    def wrapper(func):
        def _wrapper(*args, **kwargs):
            result = []

            def _callback(*args, func=func, **kwargs):
                result.append(func(*args, **kwargs))

            thread = threading.Thread(target=_callback, args=args, kwargs=kwargs)
            thread.setDaemon(True)
            thread.start()
            thread.join(timeout)

            return result.pop() if result else None

        return _wrapper

    return wrapper(func) if func else wrapper


class ThreadingArgs:
    lock = None
    rlock = None
    condition = None
    local = None

    @classmethod
    def get_lock(cls):
        if not cls.lock:
            cls.lock = threading.Lock()
        return cls.lock

    @classmethod
    def get_condition(cls):
        if not cls.condition:
            cls.condition = threading.Condition()
        return cls.condition

    @classmethod
    def get_local(cls):
        if not cls.local:
            cls.local = threading.local()
        return cls.local


get_lock = ThreadingArgs.get_lock
get_condition = ThreadingArgs.get_condition
get_local = ThreadingArgs.get_local
