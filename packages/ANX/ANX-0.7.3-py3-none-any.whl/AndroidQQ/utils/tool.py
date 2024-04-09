import base64


def to_serializable(obj):
    # Jce解析需要递归解析

    if isinstance(obj, bytearray):
        return obj.hex()
    if isinstance(obj, dict):
        return {key: to_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [to_serializable(element) for element in obj]
    elif hasattr(obj, '__dict__'):
        return {key: to_serializable(value) for key, value in obj.__dict__.items()}
    else:
        return obj  # 基本类型


def qq_bkn(_skey: str):
    base = 5381
    for char in _skey:
        base += (base << 5) + ord(char)
    result = base & 2147483647
    return str(result)


if __name__ == '__main__':
    skey = "MspAxHssKk"
    print(qq_bkn(skey))
