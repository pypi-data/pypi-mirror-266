# -*- coding: utf-8 -*-
"""
    xpan auth
    include:
        authorization_code, just get token by code
        refresh_token
        device_code
"""
import os, sys

from .. import ApiClient
from ..api import auth_api

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)


def oauthtoken_authorizationcode(code=None, client_id=None, client_secret=None, redirect_uri="oob", **kwargs):
    """
    authorizationcode
    get token by authorization code
    """
    if kwargs.get("code"):
        code = kwargs.get("code")
    if kwargs.get("client_id"):
        client_id = kwargs.get("client_id")
    if kwargs.get("client_secret"):
        client_secret = kwargs.get("client_secret")
    if kwargs.get("redirect_uri"):
        redirect_uri = kwargs.get("redirect_uri")

    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = auth_api.AuthApi(api_client)
        # code = "3ce3370c960ce929306c419d32f92df1" # str |
        # client_id = "R2Ai3Qcsq2IYP2EXC3A8lmpkQ22iujVh" # str |
        # client_secret = "KMbyNtHpPkPq7KGGGKrQqunHRi2LMYjU" # str |

        # redirect_uri = "oob" # str |
        api_response = api_instance.oauth_token_code2token(code, client_id, client_secret, redirect_uri)
        return api_response

        # # example passing only required values which don't have defaults set
        # try:
        #     api_response = api_instance.oauth_token_code2token(code, client_id, client_secret, redirect_uri)
        #     pprint(api_response)
        # except ApiException as e:
        #     print("Exception when calling AuthApi->oauth_token_code2token: %s\n" % e)


def oauthtoken_refreshtoken(refresh_token=None, client_id=None, client_secret=None, **kwargs):
    """
    refresh access token
    """
    if kwargs.get('refresh_token'):
        refresh_token = kwargs.get('refresh_token')
    if kwargs.get('client_id'):
        client_id = kwargs.get('client_id')
    if kwargs.get('client_secret'):
        client_secret = kwargs.get('client_secret')
    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = auth_api.AuthApi(api_client)
        # refresh_token = "122.5d587a6620cf03ebd221374097d5342a.Y3l9RzmaC4A1xq2F4xQtCnhIb4Ecp0citCARk0T.Uk3m_w" # str |
        # client_id = "R2Ai3Qcsq2IYP2EXC3A8lmpkQ22iujVh" # str |
        # client_secret = "KMbyNtHpPkPq7KGGGKrQqunHRi2LMYjU" # str |
        api_response = api_instance.oauth_token_refresh_token(refresh_token, client_id, client_secret,**kwargs)
        return api_response

        # example passing only required values which don't have defaults set
        # try:
        #     api_response = api_instance.oauth_token_refresh_token(refresh_token, client_id, client_secret)
        #     pprint(api_response)
        # except ApiException as e:
        #     print("Exception when calling AuthApi->oauth_token_refresh_token: %s\n" % e)


def oauthtoken_devicecode(app_key, scope="basic,netdisk", **kwargs):
    """
    devicecode 
    get device code 
    """
    if "scope" in kwargs:
        scope = kwargs["scope"]
    if "app_key" in kwargs:
        app_key = kwargs["app_key"]
    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = auth_api.AuthApi(api_client)
        client_id = app_key  # str |
        scope = scope  # str |
        api_response = api_instance.oauth_token_device_code(client_id, scope,**kwargs)
        return api_response

        # # example passing only required values which don't have defaults set
        # try:
        #     api_response = api_instance.oauth_token_device_code(client_id, scope)
        #     # pprint(api_response)
        #     return api_response
        # except baidu_disk_openapi.ApiException as e:
        #     print("Exception when calling AuthApi->oauth_token_device_code: %s\n" % e)


def oauthtoken_devicetoken(code, app_key, secret_key, **kwargs):
    """
    get token by device code
    """

    if "code" in kwargs:
        code = kwargs["code"]
    if "app_key" in kwargs:
        app_key = kwargs["app_key"]
    if "secret_key" in kwargs:
        secret_key = kwargs["secret_key"]

    # Enter a context with an instance of the API client
    with ApiClient() as api_client:
        # Create an instance of the API class
        api_instance = auth_api.AuthApi(api_client)
        api_response = api_instance.oauth_token_device_token(code, app_key, secret_key,**kwargs)
        return api_response

        # example passing only required values which don't have defaults set
        # try:
        #     api_response = api_instance.oauth_token_device_token(code, client_id, client_secret)
        #     pprint(api_response)
        #     return api_response
        # except baidu_disk_openapi.ApiException as e:
        #     print("Exception when calling AuthApi->oauth_token_device_token: %s\n" % e)
