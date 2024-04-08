# -*- coding: utf-8 -*-
import re
import sys

import oss2
import requests
import shortuuid
import urllib3
from oss2 import determine_part_size, SizedFileAdapter
from oss2.models import PartInfo

HTTP_POOL = urllib3.PoolManager(cert_reqs='CERT_NONE')
import urllib.parse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AliyunOSS(object):
    def __init__(self, accesskey_id, accesskey_secret, endpoint, bucket, domian, **kwargs):

        self.__dict__.update(locals())

        self.key_id = accesskey_id
        self.key_secret = accesskey_secret
        self.endpoint = endpoint
        self.bucket_name = bucket
        self.domian = domian

        auth = oss2.Auth(self.key_id, self.key_secret)
        self.bucket = oss2.Bucket(auth, self.endpoint, self.bucket_name)

    def upload_data(self, data, oss_key,
                    headers=None,
                    progress_callback=None):

        """
        上传一个普通文件。
        用法 ::
            >>> bucket.put_object('readme.txt', 'content of readme.txt')
            >>> with open(u'local_file.txt', 'rb') as f:
            >>>     AliyunOSS.upload_data('remote_file.txt', f)
        :param key: 上传到OSS的文件名

        :param data: 待上传的内容。
        :type data: bytes，str或file-like object

        :param headers: 用户指定的HTTP头部。可以指定Content-Type、Content-MD5、x-oss-meta-开头的头部等
        :type headers: 可以是dict，建议是oss2.CaseInsensitiveDict

        :param progress_callback: 用户指定的进度回调函数。可以用来实现进度条等功能。参考 :ref:`progress_callback` 。

        :return: :class:`PutObjectResult <oss2.models.PutObjectResult>`
        """

        self.bucket.put_object(oss_key, data, headers, progress_callback)
        path = self.domian + "/" + urllib.parse.quote(oss_key)
        return path

    def upload_from_local_file(
            self, local_file_path, oss_key,
            headers=None,
            progress_callback=None
    ) -> str:
        '''
        将文件上传到oss上
        :param local_file_path: 要上传的文件
        :param oss_key: oss上的路径, 要存在oss上的那个文件
        :return:
        '''

        # 上传
        res = self.bucket.put_object_from_file(oss_key, local_file_path, headers, progress_callback)
        path = self.domian + "/" + urllib.parse.quote(oss_key)
        return path

    def upload_from_url(self, url, oss_key, headers=None, progress_callback=None) -> str:

        # 从url下载文件
        response = requests.get(url, stream=True, verify=False)
        total_size = int(response.headers.get('content-length', 0))
        filename = None
        content_disposition = response.headers.get('content-disposition')
        if content_disposition:
            match = re.search(r'filename="(.+?)"', content_disposition)
            if match:
                filename = match.group(1)

        if not filename:
            filename = url.rsplit('/', 1)[-1]

        filename = urllib.parse.unquote(filename)

        # 定义不允许的字符正则表达式
        illegal_chars = r'[\\/:"*?<>|]'
        # 替换非法字符为空格
        filename = re.sub(illegal_chars, '_', filename)

        if oss_key.endswith('/'):
            oss_key = oss_key + filename

        # with open(output_path, 'wb') as f, tqdm(
        #     total=total_size, unit='iB', unit_scale=True, ncols=80
        # ) as progress_bar:
        #     for data in response.iter_content(chunk_size=1024):
        #         size = f.write(data)
        #         progress_bar.update(size)

        # 上传文件

        # total_size = os.path.getsize(filename)
        chunk_size = 1024*100
        # determine_part_size方法用于确定分片大小。
        part_size = determine_part_size(total_size, preferred_size=chunk_size)

        # 初始化分片。
        # 如需在初始化分片时设置文件存储类型，请在init_multipart_upload中设置相关Headers，参考如下。
        # headers = dict()
        # 指定该Object的网页缓存行为。
        # headers['Cache-Control'] = 'no-cache'
        # 指定该Object被下载时的名称。
        # headers['Content-Disposition'] = 'oss_MultipartUpload.txt'
        # 指定该Object的内容编码格式。
        # headers['Content-Encoding'] = 'utf-8'
        # 指定过期时间，单位为毫秒。
        # headers['Expires'] = '1000'
        # 指定初始化分片上传时是否覆盖同名Object。此处设置为true，表示禁止覆盖同名Object。
        # headers['x-oss-forbid-overwrite'] = 'true'
        # 指定上传该Object的每个Part时使用的服务器端加密方式。
        # headers[OSS_SERVER_SIDE_ENCRYPTION] = SERVER_SIDE_ENCRYPTION_KMS
        # 指定Object的加密算法。如果未指定此选项，表明Object使用AES256加密算法。
        # headers[OSS_SERVER_SIDE_DATA_ENCRYPTION] = SERVER_SIDE_ENCRYPTION_KMS
        # 表示KMS托管的用户主密钥。
        # headers[OSS_SERVER_SIDE_ENCRYPTION_KEY_ID] = '9468da86-3509-4f8d-a61e-6eab1eac****'
        # 指定Object的存储类型。
        # headers['x-oss-storage-class'] = oss2.BUCKET_STORAGE_CLASS_STANDARD
        # 指定Object的对象标签，可同时设置多个标签。
        # headers[OSS_OBJECT_TAGGING] = 'k1=v1&k2=v2&k3=v3'
        # upload_id = bucket.init_multipart_upload(key, headers=headers).upload_id
        upload_id = self.bucket.init_multipart_upload(oss_key).upload_id
        parts = []

        # 逐个上传分片。
        part_number = 1
        offset = 0
        consumed_bytes = 0
        for data in response.iter_content(chunk_size=chunk_size):
            if offset < total_size:

                # size = f.write(data)
                # progress_bar.update(size)


                # data_bytes = data
                # rate = int(100 * (float(consumed_bytes) / float(total_size)))
                # print('\rdownloading {0}% '.format(rate), end='')
                # sys.stdout.flush()

                num_to_upload = min(part_size, total_size - offset)
                # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
                #                                key,     upload_id, part_number, data,                   progress_callback
                # result = self.bucket.upload_part(oss_key, upload_id, part_number, SizedFileAdapter(data, num_to_upload))
                result = self.bucket.upload_part(oss_key, upload_id, part_number, data)
                parts.append(PartInfo(part_number, result.etag))

                consumed_bytes += len(data)
                progress_callback(consumed_bytes, total_size,filename)


            offset += num_to_upload
            part_number += 1


        # with open(filename, 'rb') as fileobj:
        #     part_number = 1
        #     offset = 0
        #     while offset < total_size:
        #         num_to_upload = min(part_size, total_size - offset)
        #         # 调用SizedFileAdapter(fileobj, size)方法会生成一个新的文件对象，重新计算起始追加位置。
        #         result = bucket.upload_part(key, upload_id, part_number,
        #                                     SizedFileAdapter(fileobj, num_to_upload))
        #         parts.append(PartInfo(part_number, result.etag))
        #
        #         offset += num_to_upload
        #         part_number += 1

        # 完成分片上传。
        # 如需在完成分片上传时设置相关Headers，请参考如下示例代码。
        headers = dict()
        # 设置文件访问权限ACL。此处设置为OBJECT_ACL_PRIVATE，表示私有权限。
        # headers["x-oss-object-acl"] = oss2.OBJECT_ACL_PRIVATE
        self.bucket.complete_multipart_upload(oss_key, upload_id, parts, headers=headers)
        # bucket.complete_multipart_upload(key, upload_id, parts)

        path = self.domian + "/" + urllib.parse.quote(oss_key)
        return path


    # 判断文件在不在
    def oss_file_exist(self, oss_key) -> dict:
        return self.bucket.object_exists(oss_key)

    def upload_feishu_file(self, feishu, feishu_file_item, oss_key_or_folder, headers=None,
                           progress_callback=None) -> str:
        '''
        上传飞书文件
        :param oss_key_or_folder: 如果是以/结尾的, 则是文件夹, 否则是文件
        :param feishu_file_item:
            {
                "file_token": "Vl3FbVkvnowlgpxpqsAbBrtFcrd",
                "name": "飞书.jpeg",
                "size": 32975,
                "tmp_url": "https://open.feishu.cn/open-apis/drive/v1/medias/batch_get_tmp_download_url?file_tokens=Vl3FbVk11owlgpxpqsAbBrtFcrd&extra=%7B%22bitablePerm%22%3A%7B%22tableId%22%3A%22tblBJyX6jZteblYv%22%2C%22rev%22%3A90%7D%7D",
                "type": "image/jpeg",
                "url": "https://open.feishu.cn/open-apis/drive/v1/medias/Vl3FbVk11owlgpxpqsAbBrtFcrd/download?extra=%7B%22bitablePerm%22%3A%7B%22tableId%22%3A%22tblBJyX6jZteblYv%22%2C%22rev%22%3A90%7D%7D"
			}
        :param headers:
        :param progress_callback:
        :return:
        '''

        oss_key = oss_key_or_folder
        if oss_key.endswith("/"):
            oss_key = oss_key_or_folder + feishu_file_item['name']
        if not headers:
            headers = {'Content-Type': feishu_file_item['type']}

        file_token = feishu_file_item.get('file_token')
        download_url = feishu.medias_batch_get_tmp_download_url(file_tokens=file_token)
        tmp_download_url = download_url.get("tmp_download_urls")[0].get('tmp_download_url')
        return self.upload_from_url(tmp_download_url, oss_key, headers=headers, progress_callback=progress_callback)

    def download_content_bytes(self, key):
        # 下载文件
        result = self.bucket.get_object(key)
        content_got = b''
        for chunk in result:
            content_got += chunk
        return content_got

    def download_to_local(self, key, local_path):
        res = self.bucket.get_object_to_file(key, local_path)
        return res

    def download_stream(self, key):
        object_stream = self.bucket.get_object(key)
        return object_stream
        # print(object_stream.read())
        # # 由于get_object接口返回的是一个stream流，需要执行read()后才能计算出返回Object数据的CRC checksum，因此需要在调用该接口后进行CRC校验。
        # if object_stream.client_crc != object_stream.server_crc:
        #     print("The CRC checksum between client and server is inconsistent!")

    def list_obj(self, **kwargs):
        bucket = kwargs.get("bucket")
        if not bucket:
            bucket = self.bucket
        kwargs.pop("bucket")
        files = []
        for obj in oss2.ObjectIterator(bucket, **kwargs):
            files.append(obj)
        return files

    def list_files(self, prefix, delimiter='/', marker='', bucket=None):
        """
        :param marker: 文件后缀
        :param prefix: 文件前缀，'fun/'
        :param delimiter:
        :param bucket:
        :return:
        """
        params = {
            "bucket": bucket,
            "delimiter": delimiter,
            "prefix": prefix,
            "marker": marker
        }
        objects = self.list_obj(**params)
        return objects
