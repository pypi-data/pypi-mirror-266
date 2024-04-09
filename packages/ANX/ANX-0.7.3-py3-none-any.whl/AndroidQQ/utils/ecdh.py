"""加密工具。

该模块用于使用 ECDH 或会话票证加密来加密数据。

：版权所有：版权所有(C)2021-2021 cscs181
：许可证：AGPL-3.0 或更高版本。有关详细信息，请参阅“许可证”。

.. _LICENSE:
    https://github.com/cscs181/CAI/blob/master/LICENSE
"""
from hashlib import md5

from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat


def get_ecdh():
    _p256 = ec.SECP256R1()
    svr_public_key = ec.EllipticCurvePublicKey.from_encoded_point(
        _p256,
        bytes.fromhex(
            "04"
            "EBCA94D733E399B2DB96EACDD3F69A8BB0F74224E2B44E3357812211D2E62EFB"
            "C91BB553098E25E33A799ADC7F76FEB208DA7C6522CDB0719A305180CC54A82E"
        ),
    )

    client_private_key = ec.generate_private_key(_p256)
    client_public_key = client_private_key.public_key().public_bytes(
        Encoding.X962, PublicFormat.UncompressedPoint
    )

    share_key = md5(
        client_private_key.exchange(ec.ECDH(), svr_public_key)[:16]
    ).digest()

    return client_public_key, share_key
