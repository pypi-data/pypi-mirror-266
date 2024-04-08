# -*- coding: utf-8 -*-
import json
import os
import re
import sys
import time


import urllib3

from .baidu_disk import ApiException
from .baidu_disk.utils.auth import oauthtoken_devicecode, oauthtoken_devicetoken, oauthtoken_refreshtoken
from .baidu_disk.utils.fileinfo import filelist
from .baidu_disk.utils.filemanager import move, copy, rename, delete, create_folder
from .baidu_disk.utils.multimedia_file import listall, filemetas

HTTP_POOL = urllib3.PoolManager(cert_reqs='CERT_NONE')
import urllib.parse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class Baidudisk(object):
    def __init__(self, app_key, secret_key, tenant=None,cache_path = "./tmp", **kwargs):
        # self.__dict__.update(locals())

        self.cache_path = kwargs.get("cash_path", cache_path)
        # 如果cache_path不存在，创建cache_path
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

        self.tenant = tenant
        self.app_key = kwargs.get("app_key", app_key)
        self.secret_key = kwargs.get("secret_key", secret_key)
        self.scope = kwargs.get("scope", "basic netdisk")

        self.device_code = self.__get_cahced_token("device_code")
        self.access_token = self.__get_cahced_token("access_token")
        self.refresh_token = self.__get_cahced_token("refresh_token")
        expires_at_str = self.__get_cahced_token("expires_at")
        self.expires_at = int(expires_at_str) if expires_at_str else None

    def __refresh_cached_properties(self):
        self.device_code = self.__get_cahced_token("device_code")
        self.access_token = self.__get_cahced_token("access_token")
        self.refresh_token = self.__get_cahced_token("refresh_token")
        expires_at_str = self.__get_cahced_token("expires_at")
        self.expires_at = int(expires_at_str) if expires_at_str else None

    def __get_cahced_token(self,key):
        file = os.path.join(self.cache_path, f"baidunetdisk_{self.tenant}.json")
        if not os.path.exists(file):
            return None
        else:
            with open(file, "r") as f:
                property = json.loads(f.read())
                return property.get(key, None)

    def __cahce_property(self, key, value):
        file = os.path.join(self.cache_path, f"baidunetdisk_{self.tenant}.json")
        property = {}
        if not os.path.exists(file):
            property[key] = value
            with open(file, "w") as f:
                f.write(json.dumps(property, indent=4, ensure_ascii=False))
        else:
            with open(file, "r") as f:
                property = json.loads(f.read())
                property[key] = value
            with open(file, "w") as f:
                f.write(json.dumps(property, indent=4, ensure_ascii=False))
        self.__refresh_cached_properties()


    def is_auth(self):
        # 如果expires_at大于当前时间，说明token还有效，self.is_auth = True
        now = int(time.time())
        # print("expires_at", self.expires_at, "now", now,  self.expires_at-now)
        is_auth = self.expires_at is not None and self.expires_at > int(time.time())
        return is_auth


    def __check_token(self):
        # 刷新token
        now = int(time.time())
        # print("expires_at", self.expires_at, "now", now, self.expires_at - now)
        if self.expires_at is None:
            raise TokenExpiredException(reason=f"token is expired，please login again")
        if self.expires_at < int(time.time()):
            self.__refresh_token()
        # refresh_token=None, client_id=None, client_secret=None


    def __refresh_token(self):
        res = oauthtoken_refreshtoken(self.refresh_token, self.app_key, self.secret_key)
        # {'access_token': '126.2ec0ffa6456c0e5515cbe46e4297f014.Ymbb6R_6H8pWSBVcD2Fit-wGES4JZq7fXHft0SQ.mp6MJQ',
        #  'expires_in': 2592000,
        #  'refresh_token': '127.134b97eabe45b32566c3d1303410c824.YQZeqmaL4hSEwkAM41Kt1njmUlo28zYGv9e-4iQ.ScjUbg',
        #  'scope': 'basic netdisk',
        #  'session_key': '',
        #  'session_secret': ''}
        # self.access_token = res["access_token"]
        self.__cahce_property("access_token", res["access_token"])
        # self.refresh_token = res["refresh_token"]
        self.__cahce_property("refresh_token", res["refresh_token"])
        # self.expires_at = time.time() + res["expires_in"]
        self.__cahce_property("expires_at", time.time() + res["expires_in"])

    def show_qr(self):
        # 1.扫码登录
        res = oauthtoken_devicecode(self.app_key)
        # {'device_code': '0993010f33712ad7ff2de4ff76db2f2e',
        #  'expires_in': 300,
        #  'interval': 5,
        #  'qrcode_url': 'https://openapi.baidu.com/device/qrcode/6ad8f3eb08e1f9ceb1e3d9958c6e9807/bhaq4ptd',
        #  'user_code': 'bhaq4ptd',
        #  'verification_url': 'https://openapi.baidu.com/device'}
        self.__cahce_property("device_code",res["device_code"])
        return res

    def auth_by_qr(self):
        p = {
            "code": self.device_code,
            "app_key": self.app_key,
            "secret_key": self.secret_key
        }
        res = oauthtoken_devicetoken(**p)
        # {'access_token': '126.6f1888128811faed7a5a45b19d079d25.YBgHQjzHXZ8h9iS8RnQWSoTIHJSVq6zQurCOA4S.LpU-Rw',
        #  'expires_in': 2592000,
        #  'refresh_token': '127.5bc340f665c2c68e1af7a72f12932054.YsjmXD3Dhe55NRkMBLxyFLUWgNKYIq0SJ0f6Qk5.7Cz82A',
        #  'scope': 'basic netdisk',
        #  'session_key': '',
        #  'session_secret': ''}
        # self.access_token = res["access_token"]
        self.__cahce_property("access_token",res["access_token"])
        # self.refresh_token = res["refresh_token"]
        self.__cahce_property("refresh_token",res["refresh_token"])
        # self.expires_at = int(time.time())  + res["expires_in"]
        self.__cahce_property("expires_at",int(time.time()) + res["expires_in"])
        return res

    def filelist(self, dir="/", folder="1", start=0, limit=1000, order="time", desc=1, web="1",showempty=1, **kwargs):
        """
        :param dir:			string	否	%2F%E6%B5%8B%E8%AF%95%E7%9B%AE%E5%BD%95	URL参数	需要list的目录，以/开头的绝对路径, 默认为/
        :param 							路径包含中文时需要UrlEncode编码
        :param 							给出的示例的路径是/测试目录的UrlEncode编码
        :param order:		string	否	name	URL参数	排序字段：默认为name；
        :param 							time表示先按文件类型排序，后按修改时间排序；
        :param 							name表示先按文件类型排序，后按文件名称排序；(注意，此处排序是按字符串排序的，如果用户有剧集排序需求，需要自行开发)
        :param 							size表示先按文件类型排序，后按文件大小排序。
        :param desc:		int		否	1	URL参数	默认为升序，设置为1实现降序 （注：排序的对象是当前目录下所有文件，不是当前分页下的文件）
        :param start:		int		否	0	URL参数	起始位置，从0开始
        :param limit:		int		否	100	URL参数	查询数目，默认为1000，建议最大不超过1000
        :param web:			int		否	1	URL参数	值为1时，返回dir_empty属性和缩略图数据
        :param folder:		int		否	0	URL参数	是否只返回文件夹，0 返回所有，1 只返回文件夹，且属性只返回path字段
        :param showempty:	int		否	0	URL参数	是否返回dir_empty属性，0 不返回，1 返回

        :return:
            {'errno': 0,
             'guid': 0,
             'guid_info': '',
             'list': [
                      {'dir_empty': 1,
                       'fs_id': 0,
                       'path': '/betterme/0200董晨宇的传播学课_L6798',
                       'share': 0}
                      ],
             'request_id': 9105102554915445232}
        """
        self.__check_token()
        # dir="/", folder="0", start="0", limit=2, order="time", desc=1, web="web"
        return filelist(self.access_token, dir, folder, str(start), limit, order, desc, web,showempty, **kwargs)

    def filelist_by_page(self, dir="/", folder="1", page_no=1, page_size=1000, order="name", desc=0, web="1", **kwargs):
        """
        :param dir: 需要list的目录，以/开头的绝对路径, 默认为/
                    路径包含中文时需要UrlEncode编码
                    给出的示例的路径是/测试目录的UrlEncode编码
        :param folder: 是否只返回文件夹，0 返回所有，1 只返回文件夹，且属性只返回path字段
        :param page_no: 页码
        :param page_size: 每页数量
        :param order: 排序字段：默认为name；
        :param desc: 默认为升序，设置为1实现降序 （注：排序的对象是当前目录下所有文件，不是当前分页下的文件）
        :param web: 值为1时，返回dir_empty属性和缩略图数据
        :return:
            {'errno': 0,
             'guid': 0,
             'guid_info': '',
             'list': [
                      {'dir_empty': 1,
                       'fs_id': 0,
                       'path': '/betterme/0200董晨宇的传播学课_L6798',
                       'share': 0}
                      ],
             'request_id': 9105102554915445232}
        """
        start = (page_no - 1) * page_size
        limit = page_size
        return self.filelist(dir, folder, start, limit, order, desc, web, **kwargs)

    def listall(self, path="/", recursion=1, web="1", start=0, limit=2, order="time", desc=1, ctime=None,mtime=None,device_id=None,**kwargs):
        """
        :param path:		string	是	%2F%E6%B5%8B%E8%AF%95%E7%9B%AE%E5%BD%95	URL参数	目录名称绝对路径，必须/开头；
                                            路径包含中文时需要UrlEncode编码 ；
                                            给出的示例的路径是/测试目录的UrlEncode编码。
        :param recursion:	int		否	0	URL参数	是否递归，0为否，1为是，默认为0
        :param order:		string	否	time	URL参数	排序字段:time(修改时间)，name(文件名，注意，此处排序是按字符串排序的，如果用户有剧集排序需求，需要自行开发)，size(大小，目录无大小)，默认为文件类型
        :param desc:		string	否	0	URL参数	0为升序，1为降序，默认为0
        :param start:		int		否	0	URL参数	查询起点，默认为0，当返回has_more=1时，应使用返回的cursor作为下一次查询的起点
        :param limit:		int		否	1000	URL参数	查询数目，默认为1000；
                                            如果设置start和limit参数，则建议最大设置为1000
        :param ctime:		int		否	1609430400	URL参数	文件上传时间，设置此参数，表示只返回上传时间大于ctime的文件
        :param mtime:		int		否	1619798400	URL参数	文件修改时间，设置此参数，表示只返回修改时间大于mtime的文件
        :param web:			int		否	0	URL参数	默认为0， 为1时返回缩略图地址
        :param device_id:	string	否，硬件设备必传	144213733w02217w8v	URL参数	设备ID，硬件设备必传
        :param kwargs:
        :return:
        """
        self.__check_token()
        return listall(self.access_token, path, recursion, web, start, limit, order, desc, ctime,mtime,device_id,**kwargs)

    def listall_by_page(self, path="/", recursion=1, web="1", page_no=1, page_size=1000, order="name", desc=0, **kwargs):
        """
        :param path: 需要list的目录，以/开头的绝对路径, 默认为/
                    路径包含中文时需要UrlEncode编码
                    给出的示例的路径是/测试目录的UrlEncode编码
        :param recursion: 是否递归，默认为1
        :param web: 值为1时，返回dir_empty属性和缩略图数据
        :param page_no: 页码
        :param page_size: 每页数量
        :param order: 排序字段：默认为name；
        :param desc: 默认为升序，设置为1实现降序 （注：排序的对象是当前目录下所有文件，不是当前分页下的文件）
        :return:
            {'errno': 0,
             'guid': 0,
             'guid_info': '',
             'list': [
                      {'dir_empty': 1,
                       'fs_id': 0,
                       'path': '/betterme/0200董晨宇的传播学课_L6798',
                       'share': 0}
                      ],
             'request_id': 9105102554915445232}
        """
        start = (page_no - 1) * page_size
        limit = page_size
        return self.listall(path, recursion, web, start, limit, order, desc, **kwargs)

    def filemetas(self, fsids, thumb=1, extra=1, dlink=1, needmedia=1, **kwargs):
        """

        :param fsids:		array	是	[414244021542671,633507813519281]	URL参数	文件id数组，数组中元素是uint64类型，数组大小上限是：100
        :param dlink:		int	    否	0	URL参数	是否需要下载地址，0为否，1为是，默认为0。获取到dlink后，参考下载文档进行下载操作
        :param path:		string	否	/123-571234	URL参数	查询共享目录或专属空间内文件时需要。
                                            共享目录格式： /uk-fsid
                                            其中uk为共享目录创建者id， fsid对应共享目录的fsid
                                            专属空间格式：/_pcs_.appdata/xpan/
        :param thumb:		int		否	0	URL参数	是否需要缩略图地址，0为否，1为是，默认为0
        :param extra:		int		否	0	URL参数	图片是否需要拍摄时间、原图分辨率等其他信息，0 否、1 是，默认0
        :param needmedia:	int		否	0	URL参数	视频是否需要展示时长信息，needmedia=1时，返回 duration 信息时间单位为秒 （s），转换为向上取整。
                                        0 否、1 是，默认0
        :param kwargs:
        :return:
        """
        self.__check_token()
        return filemetas(self.access_token, fsids, thumb, extra, dlink, needmedia, **kwargs)

    def filemetas1(self, fsid, thumb=1, extra=1, dlink=0, needmedia=1, **kwargs):
        """
        :param fsid:  文件id
        :param thumb:  是否需要缩略图地址，0为否，1为是，默认为0
        :param extra:  图片是否需要拍摄时间、原图分辨率等其他信息，0 否、1 是，默认0
        :param dlink:  是否需要下载地址，0为否，1为是，默认为0。获取到dlink后，参考下载文档进行下载操作
        :param needmedia:   视频是否需要展示时长信息，needmedia=1时，返回 duration 信息时间单位为秒 （s），转换为向上取整。
        :param kwargs:
        :return:
        """
        fsids = [fsid]
        return filemetas(self.access_token, fsids, thumb, extra, dlink, needmedia, **kwargs)

    def move(self, filelist, ondup="overwrite", _async=1, **kwargs):
        """
        :param filelist:json array	是  [{"path":"/test/123456.docx","dest":"/test/abc","newname":"123456.docx","ondup":"overwrite"}]
        :param async:	int		    是	1	RequestBody参数	0 同步，1 自适应，2 异步
        :param ondup:	string	    否	overwrite	RequestBody参数	全局ondup,遇到重复文件的处理策略,
                                            fail(默认，直接返回失败)、newcopy(重命名文件)、overwrite、skip
        :param kwargs:
        :return:
        """
        # filelist = '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123456.docx","ondup":"overwrite"}]'
        self.__check_token()
        # filelist, ondup="overwrite",_async=1
        return move(self.access_token, filelist, ondup, _async, **kwargs)

    def move1(self, path, dest, newname=None, ondup="overwrite", _async=1, **kwargs):
        """
        :param path: 原始路径
        :param dest:  目标路径
        :param newname:  新文件名，如果不传，则默认为原文件名
        :param ondup:  重复文件处理策略
        :param _async:  是否异步
        :param kwargs:
        :return:
        """
        # filelist = '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123456.docx","ondup":"overwrite"}]'
        if newname is None:
            newname = os.path.basename(path)
        filelist = [{"path": path, "dest": dest, "newname": newname, "ondup": ondup}]
        return self.move(filelist, ondup, _async, **kwargs)

    def copy(self, filelist, _async=1, **kwargs):
        """
        :param filelist:  json array	是  [{"path":"/test/123456.docx","dest":"/test/abc","newname":"123.docx","ondup":"overwrite"}]
        :param _async:  int	是	1	RequestBody参数	0 同步，1 自适应，2 异步
        :param kwargs:
        :return:
        """
        # filelist = '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123.docx","ondup":"overwrite"}]'
        self.__check_token()
        return copy(self.access_token, filelist, _async, **kwargs)

    def copy1(self, path, dest, newname=None, ondup="overwrite", _async=1, **kwargs):
        """
        :param path: 原始路径
        :param dest:  目标路径
        :param newname:  新文件名，如果不传，则默认为原文件名
        :param ondup:  重复文件处理策略
        :param _async:  是否异步
        :param kwargs:
        :return:
        """
        # filelist = '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123.docx","ondup":"overwrite"}]'
        if newname is None:
            newname = os.path.basename(path)
        filelist = [{"path": path, "dest": dest, "newname": newname, "ondup": ondup}]
        return self.copy(filelist, _async, **kwargs)

    def rename(self, filelist, ondup="overwrite", _async=1, **kwargs):
        """
        :param filelist: json array	是  [{"path":"/test/123456.docx","newname":"123.docx"}]
        :param ondup:  string	否	overwrite	RequestBody参数	全局ondup,遇到重复文件的处理策略,

        :param _async: int	是	1	RequestBody参数	0 同步，1 自适应，2 异步
        :param kwargs:
        :return:
        """
        # filelist = '[{"path":"/test/123456.docx","newname":"123.docx"}]'  # str | filelist
        self.__check_token()
        return rename(self.access_token, filelist, ondup, _async, **kwargs)

    def rename1(self, path, newname, ondup="overwrite", _async=1, **kwargs):
        """
        :param path: 原始路径
        :param newname:  新文件名
        :param ondup:  重复文件处理策略
        :param _async:  是否异步
        :param kwargs:
        :return:
        """
        # filelist = '[{"path":"/test/123456.docx","newname":"123.docx"}]'  # str | filelist
        filelist = [{"path": path, "newname": newname}]
        return self.rename(filelist, ondup, _async, **kwargs)

    def delete(self, filelist, ondup="overwrite", _async=1, **kwargs):
        """
        :param filelist: json array	是  [{"path":"/test/123456.docx"}]
        :param ondup:  string	否	overwrite	RequestBody参数	全局ondup,遇到重复文件的处理策略,
        :param _async:  int	是	1	RequestBody参数	0 同步，1 自适应，2 异步
        :param kwargs:
        :return:
        """
        # filelist = '[{"path":"/test/123456.docx"}]'  # str | filelist
        self.__check_token()
        return delete(self.access_token, filelist, ondup, _async, **kwargs)

    def delete1(self, path, ondup="overwrite", _async=1, **kwargs):
        """
        :param path: 要删除的文件路径
        :param ondup:  重复文件处理策略
        :param _async: 是否异步
        :param kwargs:
        :return:
        """
        filelist = [{"path": path}]
        return self.delete(filelist, ondup, _async, **kwargs)

    def create_folder(self, path, rtype=0,local_ctime=None, local_mtime=None, mode=None,**kwargs):
        """
        :param access_token:	string	是	12.a6b7dbd428f731035f771b8d15063f61.86400.1292922000-2346678-124328	接口鉴权认证参数，标识用户
        :param path:	string	是	/apps/appName/mydir	创建文件夹的绝对路径，需要urlencode
        :param isdir:	string	是	1	本接口固定为1
        :param rtype:	int	否	1	文件命名策略，默认0
                        0 为 不重命名，返回冲突
                        1 为 只要path冲突即重命名
                        2 为 path冲突且block_list不同才重命名
                        3 为 覆盖，需要与预上传precreate接口中的rtype保持一致
        :param local_ctime:	int	否	1596009229	客户端创建时间(精确到秒)，默认为当前时间戳
        :param local_mtime:	int	否	1596009229	客户端修改时间(精确到秒)，默认为当前时间戳
        :param mode:	int	否	1	上传方式
                        1 手动、2 批量上传、3 文件自动备份
                        4 相册自动备份、5 视频自动备份
        :param kwargs:
        :return:
        """
        self.__encode_path(path, **kwargs)
        self.__check_token()
        return create_folder(self.access_token, path, isdir=1, rtype=rtype, local_ctime=local_ctime,
                             local_mtime=local_mtime, mode=mode, **kwargs)

class TokenExpiredException(ApiException):
    """
    class UnauthorizedException
    """

    def __init__(self, status=None, reason=None, http_resp=None):
        """
        __init__
        """
        super(TokenExpiredException, self).__init__(status, reason, http_resp)
