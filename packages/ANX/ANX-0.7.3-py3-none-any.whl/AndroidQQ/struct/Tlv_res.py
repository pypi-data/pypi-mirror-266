from AndTools import pack_u
from pydantic import BaseModel

from AndroidQQ import log


def filter_none(data):
    if isinstance(data, dict):
        new_dict = {}
        for k, v in data.items():
            if v is not None and v != '' and v != b'':
                if isinstance(v, dict) or isinstance(v, list):
                    v = filter_none(v)
                new_dict[k] = v
        return new_dict
    elif isinstance(data, list):
        new_list = []
        for item in data:
            if item is not None and item != '' and item != b'':
                if isinstance(item, dict) or isinstance(item, list):
                    item = filter_none(item)
                new_list.append(item)
        return new_list
    return data


def Un_T146(_data):
    _data = _data[4:]
    pack = pack_u(_data)
    _len = pack.get_short()
    title = pack.get_bin(_len)
    _len = pack.get_short()
    message = pack.get_bin(_len)
    return {'title': title.decode(), 'message': message.decode()}


def Un_T512(Buffer: bytes):
    pack = pack_u(Buffer)
    count = pack.get_short()
    p_skey_list = {}
    for i in range(count):
        len = pack.get_short()
        name = pack.get_bin(len)
        len = pack.get_short()
        P_skey = pack.get_bin(len)
        pack.get_short()
        p_skey_list.update({name.decode('utf-8'): P_skey.decode('utf-8')})
    return p_skey_list


class Un_Tlv:

    def __init__(self, data, info):
        self.info = info
        self.pack = pack_u(data)
        self.auth_info = {}
        self.handler_map = {
            '011a': lambda _data: setattr(self.info, 'uin_name', _data[5:].decode('utf-8')),
            '0120': lambda _data: setattr(self.info.cookies, 'skey', _data.decode('utf-8')),
            '0103': lambda _data: setattr(self.info.cookies, 'client_key', _data.hex()),
            '0004': lambda _data: setattr(self.info, 'uin', _data[4:].decode('utf-8')),
            '001e': lambda _data: setattr(self.info, 'key_rand', _data),  # 手表扫码返回的时候必须
            '0018': lambda _data: setattr(self.info.UN_Tlv_list, 'T018', _data),
            '0019': lambda _data: setattr(self.info.UN_Tlv_list, 'T019', _data),
            '0065': lambda _data: setattr(self.info.UN_Tlv_list, 'T065', _data),
            '0108': lambda _data: setattr(self.info.UN_Tlv_list, 'T108', _data),
            '010e': lambda _data: setattr(self.info.UN_Tlv_list, 'userSt_Key', _data),
            '0134': lambda _data: setattr(self.info.UN_Tlv_list, 'wtSessionTicketKey', _data),
            '0114': lambda _data: setattr(self.info.UN_Tlv_list, 'userStSig', _data),
            '0133': lambda _data: setattr(self.info.UN_Tlv_list, 'wtSessionTicket', _data),
            '016a': lambda _data: setattr(self.info.UN_Tlv_list, 'T16A', _data),
            '0106': lambda _data: setattr(self.info.UN_Tlv_list, 'T106', _data),
            '0143': lambda _data: setattr(self.info.UN_Tlv_list, 'D2_T143', _data),
            '010a': lambda _data: setattr(self.info.UN_Tlv_list, 'TGT_T10A', _data),
            '0146': lambda _data: setattr(self.info.UN_Tlv_list, 'T146', Un_T146(_data)),
            '0192': lambda _data: setattr(self.info.UN_Tlv_list, 'T192_captcha', _data.decode('utf-8')),
            '0104': lambda _data: setattr(self.info.UN_Tlv_list, 'T104_captcha', _data),
            '0546': lambda _data: setattr(self.info.UN_Tlv_list, 'T546_captcha', _data),
            '0512': lambda _data: setattr(self.info.cookies, 'p_skey', Un_T512(_data)),

            '0003': lambda _data: self.auth_info.__setitem__('0003', _data.decode('utf-8')),
            '0005': lambda _data: self.auth_info.__setitem__('0005', _data.decode('utf-8')),
            '0036': lambda _data: self.auth_info.__setitem__('0036', _data.decode('utf-8')),
            '0305': lambda _data: setattr(self.info, 'share_key', _data)

        }

    def _content(self, head, data):
        handler = self.handler_map.get(head)
        if handler:
            handler(data)
        else:
            # print('tlv未解析', head, data.hex())
            pass

    def get_auth_result(self):
        return self.auth_info

    def return_specified_content(self):
        data = {
            'uin_name': self.info.uin_name,
            'guid': self.info.Guid.hex(),
            'token_A2': self.info.UN_Tlv_list.T143_token_A2,
            'token_A4': self.info.UN_Tlv_list.T10A_token_A4,
            'client_key': self.info.cookies.client_key,
        }
        return data

    def unpack(self):
        count = self.pack.get_short()
        for _ in range(count):
            head = self.pack.get_bin(2).hex()
            _len = self.pack.get_short()
            _data = self.pack.get_bin(_len)
            self._content(head, _data)
        return self.info
