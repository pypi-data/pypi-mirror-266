# -*- coding: utf-8 -*-
"""
    xpan filemanager 
    include:
        filemanager move
        filemanager copy
        filemanager remove
        filemanager delete
"""
import json
import os,sys
import time

from .. import ApiClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from pprint import pprint
from ..api import filemanager_api, fileupload_api


def move(access_token,  filelist, ondup="overwrite",_async=1,**kwargs):
    """
    filemanager move
    """
    access_token = kwargs.get("access_token", access_token)
    _async = kwargs.get("_async", _async)
    filelist = kwargs.get("filelist", filelist)
    ondup = kwargs.get("ondup", ondup)

    if isinstance(filelist, list):
        filelist = json.dumps(filelist)

    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = filemanager_api.FilemanagerApi(api_client)
        # access_token = "123.56c5d1f8eedf1f9404c547282c5dbcf4.YmmjpAlsjUFbPly3mJizVYqdfGDLsBaY5pyg3qL.a9IIIQ"  # str |
        # _async = 1  # int | async
        # # str | filelist
        # filelist = '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123456.docx","ondup":"overwrite"}]'
        # ondup = "overwrite"  # str | ondup (optional)
        api_response = api_instance.filemanagermove(
            access_token, _async, filelist, ondup=ondup,**kwargs)
        return api_response

        # example passing only required values which don't have defaults set
        # and optional values
        # try:
        #     api_response = api_instance.filemanagermove(
        #         access_token, _async, filelist, ondup=ondup)
        #     print(api_response)
        # except ApiException as e:
        #     print("Exception when calling FilemanagerApi->filemanagermove: %s\n" % e)


def copy(access_token,  filelist, _async=1,**kwargs):
    """
    filemanager copy
    """
    access_token = kwargs.get("access_token", access_token)
    _async = kwargs.get("_async", _async)
    filelist = kwargs.get("filelist", filelist)
    if isinstance(filelist, list):
        filelist = json.dumps(filelist)

    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = filemanager_api.FilemanagerApi(api_client)
        # access_token = "123.56c5d1f8eedf1f9404c547282c5dbcf4.YmmjpAlsjUFbPly3mJizVYqdfGDLsBaY5pyg3qL.a9IIIQ"  # str |
        # _async = 1  # int | async
        # # str | filelist
        # filelist = '[{"path":"/test/123456.docx","dest":"/test/abc","newname":"123.docx","ondup":"overwrite"}]'
        api_response = api_instance.filemanagercopy(access_token, _async, filelist,**kwargs)
        return api_response
        # example passing only required values which don't have defaults set
        # try:
        #     api_response = api_instance.filemanagercopy(access_token, _async, filelist)
        #     print(api_response)
        # except baidu_disk_openapi.ApiException as e:
        #     print("Exception when calling FilemanagerApi->filemanagercopy: %s\n" % e)


def rename(access_token,  filelist, ondup="overwrite",_async=1,**kwargs):
    """
    filemanager rename
    """
    if type(filelist) == list:
        filelist = json.dumps(filelist)

    access_token = kwargs.get("access_token", access_token)
    _async = kwargs.get("_async", _async)
    filelist = kwargs.get("filelist", filelist)
    ondup = kwargs.get("ondup", ondup)

    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = filemanager_api.FilemanagerApi(api_client)
        # access_token = "123.56c5d1f8eedf1f9404c547282c5dbcf4.YmmjpAlsjUFbPly3mJizVYqdfGDLsBaY5pyg3qL.a9IIIQ"  # str |
        # _async = 1  # int | async
        # filelist = '[{"path":"/test/123456.docx","newname":"123.docx"}]'  # str | filelist
        # ondup = "overwrite"  # str | ondup (optional)
        api_response = api_instance.filemanagerrename(
            access_token, _async, filelist, ondup=ondup,**kwargs)
        return api_response
        # example passing only required values which don't have defaults set
        # and optional values
        # try:
        #     api_response = api_instance.filemanagerrename(
        #         access_token, _async, filelist, ondup=ondup)
        #     pprint(api_response)
        # except baidu_disk_openapi.ApiException as e:
        #     print("Exception when calling FilemanagerApi->filemanagerrename: %s\n" % e)


def delete(access_token,  filelist, ondup="overwrite",_async=1,**kwargs):
    """
    filemanager delete
    """
    access_token = kwargs.get("access_token", access_token)
    _async = kwargs.get("_async", _async)
    filelist = kwargs.get("filelist", filelist)
    ondup = kwargs.get("ondup", ondup)

    if type(filelist) == list:
        filelist = json.dumps(filelist)
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = filemanager_api.FilemanagerApi(api_client)
        # access_token = "123.56c5d1f8eedf1f9404c547282c5dbcf4.YmmjpAlsjUFbPly3mJizVYqdfGDLsBaY5pyg3qL.a9IIIQ"  # str |
        # _async = 1  # int | async
        # filelist = '[{"path":"/test/123456.docx"}]'  # str | filelist
        # ondup = "overwrite"  # str | ondup (optional)
        api_response = api_instance.filemanagerdelete(
            access_token, _async, filelist, ondup=ondup,**kwargs)
        return api_response
        # example passing only required values which don't have defaults set
        # and optional values
        # try:
        #     api_response = api_instance.filemanagerdelete(
        #         access_token, _async, filelist, ondup=ondup)
        #     print(api_response)
        # except baidu_disk_openapi.ApiException as e:
        #     print("Exception when calling FilemanagerApi->filemanagerdelete: %s\n" % e)



def create_folder(access_token, path, isdir=1, rtype=0, local_ctime=None,local_mtime=None,mode=1,**kwargs):
    """



    """
    access_token = kwargs.get("access_token", access_token)
    path = kwargs.get("path", path)
    isdir = kwargs.get("isdir", isdir)
    rtype = kwargs.get("rtype", rtype)

    local_ctime = kwargs.get("local_ctime", local_ctime)
    local_mtime = kwargs.get("local_mtime", local_mtime)

    # if not kwargs.get("mode") is None:
    #     kwargs["mode"] = mode

    # now_time = int(time.time())
    # if local_ctime is None:
    #     local_ctime = now_time
    #     kwargs["local_ctime"] = local_ctime
    # if local_mtime is None:
    #     local_mtime = now_time
    #     kwargs["local_ctime"] = local_mtime


    #    Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = fileupload_api.FileuploadApi(api_client)
        # access_token = "123.56c5d1f8eedf1f9404c547282c5dbcf4.YmmjpAlsjUFbPly3mJizVYqdfGDLsBaY5pyg3qL.a9IIIQ"  # str |
        # path = "/apps/hhhkoo/a.txt"  # str | 对于一般的第三方软件应用，路径以 "/apps/your-app-name/" 开头。对于小度等硬件应用，路径一般 "/来自：小度设备/" 开头。对于定制化配置的硬件应用，根据配置情况进行填写。
        # isdir = 0  # int | isdir
        size = 0  # int | size
        # rtype = 3  # int | rtype (optional)

        # autoinit = 1  # int | autoinit
        # block_list = '["d05f84cf5340d1ef0c5f6d6eb8ce13b8"]' # str | 由MD5字符串组成的list


        # access_token,
        #         path,
        #         isdir,
        #         size,
        uploadid = ""
        block_list = '[]'

        api_response = api_instance.xpanfilecreate(
                access_token, path, isdir, size, uploadid, block_list, rtype=rtype,**kwargs)
        return api_response
        # example passing only required values which don't have defaults set
        # and optional values
        # try:
        #     api_response = api_instance.xpanfileprecreate(
        #         access_token, path, isdir, size, autoinit, block_list, rtype=rtype)
        #     pprint(api_response)
        # except ApiException as e:
        #     print("Exception when calling FileuploadApi->xpanfileprecreate: %s\n" % e)

if __name__ == '__main__':
    copy()
    move()
    rename()
    delete()
