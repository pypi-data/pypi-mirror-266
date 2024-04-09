def exception_factory(exception, message):
    return exception(message)


def handle_exceptions(default):
    def wrap(f):
        def inner(*a):
            try:
                return f(*a)
            except Exception:
                return default

        return inner

    return wrap
