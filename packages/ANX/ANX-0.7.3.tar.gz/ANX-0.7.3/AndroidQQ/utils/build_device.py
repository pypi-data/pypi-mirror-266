import random


def random_mac():
    return "02:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )


def random_imei():
    first14 = ''.join(str(random.randint(0, 9)) for i in range(14))
    return first14 + str((10 - sum((3, 1)[i % 2] * int(x) for i, x in enumerate(reversed(first14))) % 10) % 10)


if __name__ == "__main__":
    print(random_mac(), random_imei())

    pass
