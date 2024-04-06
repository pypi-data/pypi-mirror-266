# -*- coding: utf-8 -*-
"""
    xpan multimedia file 
    include:
        listall
        filemetas
"""
import os
import sys

from .. import ApiClient

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
from ..api import multimediafile_api


def listall(access_token,path="/",recursion=1,web="1",start=0,limit=2,order="time",desc=1,ctime=None,mtime=None,device_id=None,**kwargs):
    """
    listall
    """
    access_token = kwargs.get("access_token", access_token)
    path = kwargs.get("path", path)
    recursion = kwargs.get("recursion", recursion)
    web = kwargs.get("web", web)
    start = kwargs.get("start", start)
    limit = kwargs.get("limit", limit)
    order = kwargs.get("order", order)
    desc = kwargs.get("desc", desc)

    if ctime:
        kwargs["ctime"] = ctime
    if mtime:
        kwargs["mtime"] = mtime
    if device_id:
        kwargs["device_id"] = device_id

    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = multimediafile_api.MultimediafileApi(api_client)

        api_response = api_instance.xpanfilelistall(
            access_token, path, recursion, web=web, start=start, limit=limit, order=order, desc=desc,**kwargs)
        return api_response
        # example passing only required values which don't have defaults set
        # and optional values
        # try:
        #     api_response = api_instance.xpanfilelistall(
        #         access_token, path, recursion, web=web, start=start, limit=limit, order=order, desc=desc)
        #     pprint(api_response)
        #     return api_response
        # except baidu_disk_openapi.ApiException as e:
        #     print("Exception when calling MultimediafileApi->xpanfilelistall: %s\n" % e)


def filemetas(access_token,fsids,thumb=1,extra=1,dlink=1,needmedia=1,path="",**kwargs):
    """
    filemetas
    :param access_token:

    :return:
    """
    access_token = kwargs.get("access_token", access_token)
    fsids = kwargs.get("fsids", fsids)
    thumb = kwargs.get("thumb", thumb)
    extra = kwargs.get("extra", extra)
    dlink = kwargs.get("dlink", dlink)
    needmedia = kwargs.get("needmedia", needmedia)
    path = kwargs.get("path", path)

    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = multimediafile_api.MultimediafileApi(api_client)
        # access_token = "123.56c5d1f8eedf1f9404c547282c5dbcf4.YmmjpAlsjUFbPly3mJizVYqdfGDLsBaY5pyg3qL.a9IIIQ"  # str |
        # fsids = "[258813175385405]"  # str |
        # thumb = "1"  # str |  (optional)
        # extra = "1"  # str |  (optional)
        # dlink = "1"  # str |  (optional)
        # needmedia = 1  # int |  (optional)
        api_response = api_instance.xpanmultimediafilemetas(
            access_token, fsids, thumb=thumb, extra=extra, dlink=dlink, needmedia=needmedia,path = path,**kwargs)
        return api_response
        # example passing only required values which don't have defaults set
        # and optional values
        # try:
        #     api_response = api_instance.xpanmultimediafilemetas(
        #         access_token, fsids, thumb=thumb, extra=extra, dlink=dlink, needmedia=needmedia)
        #     pprint(api_response)
        # except baidu_disk_openapi.ApiException as e:
        #     print("Exception when calling MultimediafileApi->xpanmultimediafilemetas: %s\n" % e)


if __name__ == '__main__':
    access_token = "126.ed92850b99955145b07017ac21354fa4.Y7dVT8v40Co2b3zsCclgNY7U-dAVENAz4r5rb0D.Uj_d4w"
    listall(access_token,path="/betterme/")
    # filemetas()
