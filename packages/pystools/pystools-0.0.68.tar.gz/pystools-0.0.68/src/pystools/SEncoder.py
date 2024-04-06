import hashlib
import random
import time
import uuid
from typing import Any

import shortuuid


class SEncoder:
    @staticmethod
    def md5_from_uuid(to_upper=False):
        # 生成唯一的uuid
        v = str(uuid.uuid1())
        m = hashlib.md5()
        # 将args中的所有值拼接起来
        m.update(f"{v}".encode("utf-8"))
        if to_upper:
            return m.hexdigest().upper()
        return m.hexdigest()

    @staticmethod
    def short_uuid(to_upper=False):
        unique_id = shortuuid.uuid()
        if to_upper:
            return unique_id.upper()
        return unique_id

    @staticmethod
    def gen_md5(*args, to_upper=False):
        m = hashlib.md5()
        # 将args中的所有值拼接起来
        for arg in args:
            m.update(f"{arg}".encode("utf-8"))
        if to_upper:
            return m.hexdigest().upper()
        return m.hexdigest()

    @staticmethod
    def gen_num_str_by_timestamp(length=8):
        sleep_time = random.random() * 0.8
        print("sleep time: ", sleep_time)
        time.sleep(sleep_time)
        t = time.time()
        tm = t * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000 * 1000
        # 显示完整的数字，不用科学计数法
        tstr = "{:.0f}".format(tm)
        # print(tstr)
        nameStr = tstr[13:-1]

        def split_string(string, cnt=4):
            length = len(string)
            segment_length = length // cnt
            segments = []
            for i in range(cnt):
                start = i * segment_length
                end = (i + 1) * segment_length
                segment = string[start:end]
                segments.append(segment)
            return segments

        segments = split_string(nameStr, length)
        # print(segments)

        lid = ""
        for segment in segments:
            # 从 segment 中随机取一个字符
            char = random.choice(segment)
            # 把字符添加到 lid 中
            lid += char
        return lid

    @staticmethod
    def encode_sign(param_dict: Any, nonce: str):
        # 将param_dict中的key按照字母排序，如果只处理第一层的key，然后拼接成字符串 例如：a=1&b=2&c=3
        param_str = ""
        if isinstance(param_dict, dict):
            for key in sorted(param_dict.keys()):
                value = param_dict[key]
                value_str = value
                if not isinstance(value, str):
                    value_str = str(value)
                    if value_str == "None":
                        value_str = "null"
                param_str += f"{key}={value_str}&"
            param_str = param_str[:-1]
        # 然后将param_gen_sign.nonce拼接到字符串后面
        param_str += str(nonce)
        # 然后对字符串进行sha256加密
        import hashlib
        m = hashlib.sha256()
        m.update(param_str.encode("utf-8"))
        sign = m.hexdigest()
        return {"sign": sign, "param_str": param_str}