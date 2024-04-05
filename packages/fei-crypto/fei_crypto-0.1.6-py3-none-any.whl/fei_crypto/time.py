import datetime
import time


def dt():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def seconds():
    return round(time.time())


def milliseconds():
    return round(time.time() * 1000)


def microseconds():
    return round(time.time() * 1000 * 1000)

def nanoseconds():
    return round(time.time() * 1000 * 1000 * 1000)
