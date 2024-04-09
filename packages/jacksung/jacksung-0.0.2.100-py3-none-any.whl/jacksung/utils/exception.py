import time


def wait_fun(fun, args, catch_exception, sleep_time=1, wait_time=30):
    if wait_time <= 0:
        raise Exception(f'Wait time out until {wait_time}s')
    try:
        return fun(*args)
    except catch_exception:
        time.sleep(sleep_time)
        return wait_fun(fun, args, catch_exception, sleep_time=sleep_time, wait_time=wait_time - sleep_time)
