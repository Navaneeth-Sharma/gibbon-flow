def flow(name):
    def intermediate_func(func):
        def wrapper_func(*args, **kwargs):
            # Do something before the function.
            func(*args, **kwargs)

        return wrapper_func

    return intermediate_func


def task(name):
    def intermediate_func(func):
        def wrapper_func(*args, **kwargs):
            # Do something before the function.
            func(*args, **kwargs)

        return wrapper_func

    return intermediate_func
