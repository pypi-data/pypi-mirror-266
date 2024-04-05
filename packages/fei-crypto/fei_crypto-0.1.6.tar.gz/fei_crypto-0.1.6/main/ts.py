from fei_crypto.time import dt, seconds, milliseconds, nanoseconds


def sec():
    print(seconds())


def ms():
    print(milliseconds())


def nano():
    print(nanoseconds())


def run():
    print(dt())


if __name__ == '__main__':
    print(dt())
    print(seconds())
    print(milliseconds())
    print(nanoseconds())
