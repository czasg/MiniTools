import threading

__all__ = 'timeout',


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
