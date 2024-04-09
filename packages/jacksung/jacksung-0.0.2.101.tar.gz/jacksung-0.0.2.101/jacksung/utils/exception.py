import time


def wait_fun(fun, args, catch_exception=Exception, sleep_time=1, wait_time=30):
    try:
        return fun(*args)
    except catch_exception as e:
        if wait_time <= 0:
            raise e
        else:
            time.sleep(sleep_time)
            return wait_fun(fun, args, catch_exception, sleep_time=sleep_time, wait_time=wait_time - sleep_time)
