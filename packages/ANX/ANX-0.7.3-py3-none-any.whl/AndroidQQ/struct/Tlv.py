import struct
import time

from AndTools import pack_b, get_random_bin, get_md5, TEA, pack_u

from AndroidQQ import log
from AndroidQQ.proto import DeviceReport


def Tlv_head(head, data):
    pack = pack_b()
    pack.add_Hex(head)
    pack.add_int(len(data), 2)
    pack.add_bin(data)
    return pack.get_bytes()


class TLV:
    def __init__(self, info):
        self.pack = pack_b()
        self.info = info

    def T018(self):
        self.pack.empty()
        self.pack.add_Hex('00 01 00 00 06 00 00 00 00 10 00 00 00 00')
        self.pack.add_int(int(self.info.uin))
        self.pack.add_Hex('00 00 00 00')
        return Tlv_head('00 18', self.pack.get_bytes())

    def T001(self):
        self.pack.empty()
        self.pack.add_Hex('00 01')  # ip_version
        self.pack.add_bin(get_random_bin(4))
        self.pack.add_int(int(self.info.uin))
        self.pack.add_int(int(time.time()))  # server_time
        self.pack.add_Hex('00 00 00 00')  # ip
        self.pack.add_Hex('00 00')
        _data = self.pack.get_bytes()

        return Tlv_head('00 01', _data)

    def T017(self, app_id: int, Uin: int, login_time: int):
        self.pack.empty()
        self.pack.add_Hex('00 16 00 01')
        self.pack.add_Hex('00 00 06 00')
        self.pack.add_int(app_id)
        self.pack.add_Hex('00 00 00 00')
        self.pack.add_int(Uin)
        self.pack.add_Hex('00 00 00 00')
        return Tlv_head('00 17', self.pack.get_bytes())

    def T142(self):
        self.pack.empty()
        self.pack.add_body(self.info.device.package_name, 4)
        return Tlv_head('01 42', self.pack.get_bytes())

    def T016(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 00 05')
        self.pack.add_Hex('00 00 00 10')  # len
        self.pack.add_Hex('20 04 1E EE 9B 6B E0 65 3A 35 6F 4F AC 89 92 6F 3F 1C EB 7E')
        self.pack.add_body('com.tencent.qqlite', 2)
        self.pack.add_body('2.1.7', 2)
        self.pack.add_Hex('00 10')  # len
        self.pack.add_Hex('A6 B7 45 BF 24 A2 C2 77 52 77 16 F6 F3 6E B6 8D')
        return Tlv_head('00 16', self.pack.get_bytes())

    def T01B(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 00 00 00 00 00 00 00 00 00 08 00 00 00 04 00 00 00 48 00 00 00 02 00 00 00 02 00 00 ')
        return Tlv_head('00 1B', self.pack.get_bytes())

    def T01D(self):
        self.pack.empty()
        self.pack.add_Hex('01 00 F7 FF 7C 00 00 00 00 00 00 00 00 00')
        return Tlv_head('00 1D', self.pack.get_bytes())

    def T01F(self):
        self.pack.empty()
        self.pack.add_Hex('01')
        self.pack.add_Hex('00 07')  # android len
        self.pack.add_Hex('61 6E 64 72 6F 69 64')  # android
        self.pack.add_Hex('00 01')
        self.pack.add_Hex('39')
        self.pack.add_Hex('00 02')
        self.pack.add_Hex('00 10')  # len
        self.pack.add_Hex('43 68 69 6E 61 20 4D 6F 62 69 6C 65 20 47 53 4D')  # China Mobile GSM
        self.pack.add_Hex('00 00 00 04')
        self.pack.add_Hex('77 69 66 69')  # wifi
        return Tlv_head('00 1F', self.pack.get_bytes())

    def T033(self):
        self.pack.empty()
        self.pack.add_bin(get_random_bin(16))
        return Tlv_head('00 33', self.pack.get_bytes())

    def T035(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 00 73')
        return Tlv_head('00 35', self.pack.get_bytes())

    def T106(self):
        self.pack.empty()
        if self.info.device.client_type == 'Watch':
            self.pack.add_bin(self.info.UN_Tlv_list.T018)
            _data = self.pack.get_bytes()
            # Token0106
        else:
            password_md5 = get_md5(self.info.password.encode('utf-8'))
            hex_uin = int(self.info.uin).to_bytes(4, 'big')
            self.pack.add_Hex('00 04')  # tgtgt version
            self.pack.add_bin(get_random_bin(4))
            self.pack.add_Hex('00 00 00 12 ')  # sso_version
            self.pack.add_Hex('00 00 00 10')  # app_id
            self.pack.add_Hex('00 00 00 00')  # app_client_version
            self.pack.add_Hex('00 00 00 00')
            self.pack.add_int(int(self.info.uin))
            self.pack.add_int(self.info.login_time)
            self.pack.add_Hex('00 00 00 00 01')
            self.pack.add_bin(password_md5)
            self.pack.add_bin(self.info.key_tgtgt)
            self.pack.add_Hex('00 00 00 00 01')
            self.pack.add_bin(self.info.Guid)
            self.pack.add_int(self.info.device.app_id)
            self.pack.add_Hex('00 00 00 01')  # login_type
            self.pack.add_body(self.info.uin, 2)
            self.pack.add_Hex('00 00')
            _data = self.pack.get_bytes()

            _key = get_md5(password_md5 + bytes.fromhex('00 00 00 00') + hex_uin)
            _data = TEA.encrypt(_data, _key)

        return Tlv_head('01 06', _data)

    def T116(self, image_type=10):
        self.pack.empty()
        if self.info.device.client_type == 'Watch':
            self.pack.add_Hex('00 00 F7 FF 7C 00 01 04 00 00')
        elif self.info.device.client_type == 'QQ':
            self.pack.add_int(image_type, 2)
            self.pack.add_Hex('F7 FF 7C 00 01 04 00 01 5F 5E 10 E2')
        else:
            _data = b''
        _data = self.pack.get_bytes()

        return Tlv_head('01 16', _data)

    def T100(self, sso_version, app_id, app_client_version, sigmap):

        self.pack.empty()
        self.pack.add_Hex('00 01')
        self.pack.add_int(sso_version)
        self.pack.add_int(app_id)
        self.pack.add_int(self.info.device.app_id)
        self.pack.add_int(app_client_version)
        self.pack.add_int(sigmap)
        _data = self.pack.get_bytes()

        return Tlv_head('01 00', _data)

    def T104(self):
        _data = self.info.UN_Tlv_list.T104_captcha
        log.info("104", _data.hex())

        # _data = bytes.fromhex(
        #     '41 72 73 77 7A 7A 43 6E 6D 4E 78 4A 5A 47 69 36 42 66 78 77 46 4B 4F 33 59 5A 5A 34 44 6B 6D 69 44 67 3D 3D')
        # log.info(_data)
        # _data = b'Ai2wAWtEB75HUgAq+mzGjldzYRSjS/jceQ=='
        return Tlv_head('01 04', _data)

    def T107(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 00 00 00 01 ')
        return Tlv_head('01 07', self.pack.get_bytes())

    def T109(self):

        self.pack.empty()
        self.pack.add_bin(get_md5(self.info.device.android_id))
        return Tlv_head('01 09', self.pack.get_bytes())

    def T124(self):
        self.pack.empty()
        temp = '39'  # todo 不确定是什么,后面和普通安卓进行对比再确认
        self.pack.add_body(self.info.device.name, 2)
        self.pack.add_body(temp, 2, True)
        self.pack.add_int(2, 2)
        self.pack.add_body(self.info.device.internet, 2)
        self.pack.add_body(self.info.device.internet_type, 4)
        print(self.pack.get_bytes().hex())
        return Tlv_head('01 24', self.pack.get_bytes())

    def T128(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 01 01 00 11 00 00 00')
        self.pack.add_body(self.info.device.model, 2)
        self.pack.add_body(self.info.Guid, 2)
        self.pack.add_body(self.info.device.brand, 2)
        return Tlv_head('01 28', self.pack.get_bytes())

    def T16E(self):
        self.pack.empty()
        self.pack.add_body(self.info.device.model, 2)
        return Tlv_head('01 6E', self.pack.get_bytes())

    def T52D(self):
        device_info = DeviceReport(
            bootloader='unknown',
            proc_version='Linux version 4.4.146 (build@ubuntu) (gcc version 4.8 (GCC) ) #1 SMP PREEMPT Thu Sep 1 '
                         '18:26:33 CST 2022',
            codename='REL',
            incremental='G9650ZHU2ARC6',
            fingerprint='samsung/star2qltezh/star2qltechn:9/PQ3B.190801.002/G9650ZHU2ARC6:user/release-keys',
            boot_id=self.info.device.boot_id,
            android_id=self.info.device.android_id.hex(),
            base_band='',
            inner_version='G9650ZHU2ARC6',
        )
        return Tlv_head('05 2D', device_info.SerializeToString())

    def T144(self):
        pack = pack_b()

        if self.info.device.client_type == 'Watch':
            methods = {
                self.T109,
                self.T124,
                self.T128,
                self.T16E,
            }
        else:
            methods = {
                self.T109,
                self.T52D,
                self.T124,
                self.T128,
                self.T16E,
            }

        pack.add_int(len(methods), 2)  # 数量
        # 循环调用每一个方法，并将结果添加到包中
        for method in methods:
            pack.add_bin(method())
        _data = pack.get_bytes()
        _data = TEA.encrypt(_data, self.info.key_tgtgt)

        return Tlv_head('01 44', _data)

    def T145(self):
        """GUid"""

        return Tlv_head('01 45', self.info.Guid)

    def T147(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 00 10')
        self.pack.add_body(self.info.device.version, 2, )
        self.pack.add_body(self.info.device.Sig, 2, True)
        _data = self.pack.get_bytes()
        return Tlv_head('01 47', _data)

    def T511(self):
        """
            office.qq.com
            qun.qq.comgamecenter.qq.comdocs.qq.commail.qq.com	ti.qq.com
            vip.qq.com
            tenpay.comqqweb.qq.comqzone.qq.com
            mma.qq.comgame.qq.comopenmobile.qq.comconnect.qq.com"""

        domain = [
            'office.qq.com',
            'qun.qq.com',
            'gamecenter.qq.com',
            # 'graph.qq.com',
            # 'docs.qq.com',
            'mail.qq.com',
            'ti.qq.com',
            'vip.qq.com',
            # 'tenpay.com',
            'qqweb.qq.com',
            'qzone.qq.com',
            'mma.qq.com',
            'game.qq.com',
            # 'openmobile.qq.com',
            'connect.qq.com',
            'accounts.qq.com',
            # 'weishi.qq.com',

        ]
        self.pack.empty()
        self.pack.add_int(len(domain), 2)  # 数量
        for domain_result in domain:
            self.pack.add_Hex('01')
            self.pack.add_body(domain_result, 2)

        # print(self.pack.get_bytes().hex())

        return Tlv_head('05 11', self.pack.get_bytes())

    def T16A(self):
        self.pack.empty()
        self.pack.add_bin(self.info.UN_Tlv_list.T019)
        return Tlv_head('01 6A', self.pack.get_bytes())

    def T154(self):
        self.pack.empty()
        self.pack.add_int(self.info.seq)
        return Tlv_head('01 54', self.pack.get_bytes())

    def T141(self):
        self.pack.empty()
        self.pack.add_Hex('00 01')
        self.pack.add_body(self.info.device.internet, 2)
        self.pack.add_Hex('00 02')
        self.pack.add_body(self.info.device.internet_type, 2)
        _data = self.pack.get_bytes()
        return Tlv_head('01 41', _data)

    def T008(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 00 00 08 04 00 00')
        return Tlv_head('00 08', self.pack.get_bytes())

    def T187(self):
        Mac = get_md5(self.info.device.Mac)
        self.pack.empty()
        self.pack.add_body(Mac, 2)
        _data = self.pack.get_bytes()
        return Tlv_head('01 87', _data)

    def T188(self):
        _app_id = get_md5(str(self.info.device.app_id))

        self.pack.empty()
        self.pack.add_body(_app_id, 2)
        _data = self.pack.get_bytes()
        return Tlv_head('01 88', _data)

    def T193(self, Ticket):
        return Tlv_head('01 93', Ticket.encode())

    def T194(self):
        _IMEI = get_md5(self.info.device.Imei)
        self.pack.empty()
        self.pack.add_body(_IMEI, 2)
        return Tlv_head('01 94', self.pack.get_bytes())

    def T191(self, can_web_verify):
        self.pack.empty()

        self.pack.add_Hex(can_web_verify)

        return Tlv_head('01 91', self.pack.get_bytes())

    def T202(self):
        Bssid = get_md5(self.info.device.Bssid)
        self.pack.empty()
        self.pack.add_body(Bssid, 2)
        self.pack.add_body('<unknown ssid>', 2)
        _data = self.pack.get_bytes()
        return Tlv_head('02 02', _data)

    def T177(self):
        self.pack.empty()
        self.pack.add_Hex('01')
        self.pack.add_int(self.info.device.build_time)
        self.pack.add_body(self.info.device.sdk_version, 2)
        _data = self.pack.get_bytes()
        return Tlv_head('01 77', _data)

    def T516(self):
        self.pack.empty()
        self.pack.add_Hex('00 00 00 00')  # source_type
        return Tlv_head('05 16', self.pack.get_bytes())

    def T521(self, product_type: int):

        _data = struct.pack(">IH", product_type, 0)
        return Tlv_head('05 21', _data)

    def T525(self, _hex):
        self.pack.empty()
        self.pack.add_Hex(_hex)
        return Tlv_head('05 25', self.pack.get_bytes())

    def T318(self):
        self.pack.empty()
        self.pack.add_bin(self.info.UN_Tlv_list.T065)
        return Tlv_head('03 18', self.pack.get_bytes())

    def T544(self):
        self.pack.empty()
        self.pack.add_Hex(
            '68656861000000010100000000000000010100050000000000F3139D7900000002000000A6000100080000018A412D97310002000A7261262364366224377100030004010000010005000401000001000400040000000000060004010000040007000401000005000800040100000600090020C55E51B0542E079D3857E4E7B349855D55668F94A819085EDF5E9C4D07FFBE0B000A0010520A4AA351000C9880A69945B72FE817000B00103BB4D57F3F48F674183F22D1B307BFC6000C000401000001000D000400000000')
        return Tlv_head('05 44', self.pack.get_bytes())

    def T545(self):
        self.pack.empty()
        self.pack.add_Hex(
            '303863376639353563653831646230636361343862636135313030303137353137343062')
        return Tlv_head('05 45', self.pack.get_bytes())

    def T547(self):
        T546 = self.info.UN_Tlv_list.T546_captcha
        part1 = T546[8:]
        _pack_u = pack_u(part1)
        _len = _pack_u.get_int(2)
        part2 = _pack_u.get_bin(_len)

        add_short = int.from_bytes(part2[-2:], 'big') + 10000
        add_bin = add_short.to_bytes(2, 'big')
        part2 = part2[:-2] + add_bin

        self.pack.empty()
        self.pack.add_Hex('01 02 01 01 01 00 00 00')
        self.pack.add_bin(part1)
        self.pack.add_body(part2, 2)
        self.pack.add_Hex('00 00 00 21')
        self.pack.add_Hex('00 00 27 10')
        _data = self.pack.get_bytes()
        return Tlv_head('05 47', _data)

    def T548(self):
        self.pack.empty()
        self.pack.add_Hex(
            '01020101000A0000008079E7CD8994B25D1E7330EDB1ED1A05A64B06135BDBE39F4B06482AB4B8D1744D972DA34482C9B2C01A3D743F8AFAC78D5A77A6AE4A9B016B9C7597795EB1754EFF259A02D5725D065D4C92F46C173669CE4C7E1E06C8F8AA996C096489ECAAE767092F78E6F9C5AA284D284D05B307E824507565224BD92D12D6DF5168DFBB4B0020B9D19B2A3E26BECD3384D94C85D78914FAC6E00C2D128F5EF674F6DEB046E91B00AC01020102000A0000008079E7CD8994B25D1E7330EDB1ED1A05A64B06135BDBE39F4B06482AB4B8D1744D972DA34482C9B2C01A3D743F8AFAC78D5A77A6AE4A9B016B9C7597795EB1754EFF259A02D5725D065D4C92F46C173669CE4C7E1E06C8F8AA996C096489ECAAE767092F78E6F9C5AA284D284D05B307E824507565224BD92D12D6DF5168DFBB4B0020B9D19B2A3E26BECD3384D94C85D78914FAC6E00C2D128F5EF674F6DEB046E91B008079E7CD8994B25D1E7330EDB1ED1A05A64B06135BDBE39F4B06482AB4B8D1744D972DA34482C9B2C01A3D743F8AFAC78D5A77A6AE4A9B016B9C7597795EB1754EFF259A02')
        return Tlv_head('05 48', self.pack.get_bytes())

    def T10A(self, T0A: bytes):
        return Tlv_head('01 0A', T0A)

    def T143(self, T143: bytes):
        return Tlv_head('01 43', T143)
