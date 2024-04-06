import time


def timeit(func):
    def timed(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print("Function", func.__name__, "time:", round((end - start) * 1000, 1), "ms")
        return result

    return timed
