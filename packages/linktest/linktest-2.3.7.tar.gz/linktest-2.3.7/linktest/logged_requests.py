import os
import traceback

import json as json_func
from pprint import pformat

import requests
import settings

import curlify


def generate_curl(request):
    """
    根据 response.request 内容生产对应的 cURL
    @author: Wang Lin
    """
    command = "curl --compressed -X {method} -H {headers} -d '{data}' '{uri}'"

    method = request.method

    headers = ['"{0}: {1}"'.format(k, v) for k, v in request.headers.items()]
    headers = " -H ".join(headers)

    data = request.body
    uri = request.url

    return command.format(method=method, headers=headers, data=data, uri=uri)


class LoggedRequests:
    """
        封装 requests module 的常用方法，自动log 每次 request 的参数 & response 内容
        如果 api 有version字段 同时会log其版本信息
        @author: Wang Lin
        """

    def __init__(self, logger):
        self.logger = logger

    def log_curl(func):
        """
        log curl 装饰器
        @author: Wang Lin
        """

        def wrapper(*args, **kw):
            instance = args[0]  # 获取类实例引用
            res = func(*args, **kw)

            if not hasattr(settings, "always_generate_curl") or settings.always_generate_curl is False:
                if res.status_code == 200:
                    return res

            instance.logger.info("================================ cURL Start ==========================")
            instance.logger.info(curlify.to_curl(res.request))
            instance.logger.info("================================ cURL End ============================" + os.linesep)

            api_version = ""
            # 检查响应头部中的各种可能的版本信息
            api_version_keys = ["version", "Version", "VERSION",
                                "API-Version", "API-VERSION", "api-version",
                                "API-Version-Header", "api-version-header", "API-VERSION-HEADER"]

            # ===== log api's version =====
            for key in api_version_keys:
                if key in res.headers:
                    api_version = f"API version found in headers: {res.headers[key]}"
                    break

            if not api_version:
                # 如果未在响应头部中找到版本信息，请检查响应体中的各种可能的版本信息
                try:
                    response_body = res.json()

                    for key in api_version_keys:
                        if key in response_body:
                            api_version = f"API version found in response body: {response_body[key]}"
                            break
                except json_func.JSONDecodeError:
                    instance.logger.error(os.linesep + traceback.format_exc() + os.linesep)
                    traceback.print_exc()

            if api_version:
                instance.logger.info(os.linesep + "-------- API Version: %s" % api_version)

            return res

        return wrapper

    @log_curl
    def get(self, url, params=None, **kwargs):
        if hasattr(settings, "auto_log_request") and settings.auto_log_request is False:
            return requests.get(url, params, **kwargs)

        self.logger.info("========================= GET Request Started =========================")
        self.logger.info("URL: " + url)

        if params is not None:
            self.logger.info("params:")
            self.logger.info(pformat(params))

        if len(kwargs.keys()) > 0:
            self.logger.info("kwargs: " + os.linesep + json_func.dumps(kwargs, indent=2))

        response = requests.get(url, params, **kwargs)

        self.logger.info("<<<<<<<< GET Response:")
        self.logger.info(response)

        if response.status_code == 200:
            if 'application/json' in response.headers.get('Content-Type'):
                try:
                    data = response.json()
                    self.logger.info(os.linesep + json_func.dumps(response.json(), ensure_ascii=False, indent=2))
                except json.JSONDecodeError:
                    self.logger.error("Response is not valid JSON.")
            else:
                self.logger.info(os.linesep + response.text)

        self.logger.info("========================= GET Request Completed =========================" + os.linesep)

        return response

    @log_curl
    def post(self, url, data=None, json=None, **kwargs):
        #  为了 不重复记录 log,则 增加如下判断， 如果 settings.auto_log_request = False, 则不需要框架自动记录log!
        if hasattr(settings, "auto_log_request") and settings.auto_log_request is False:
            return requests.post(url, data, json, **kwargs)

        self.logger.info("========================= POST Request Started =========================")
        self.logger.info("URL: " + url)

        if data is not None:
            self.logger.info("POST DATA:")

            # # todo: headers type
            # if kwargs['headers']['Content-Type'] == 'application/x-www-form-urlencoded':
            #     self.logger.info(os.linesep + pformat(data))
            # else:
            #     self.logger.info(os.linesep + pformat(json_func.loads(data)))

            try:
                # 此处省去各种判断逻辑, 如果 json.loads()报错，则直接 记录原始data
                # self.logger.info(os.linesep + pformat(json_func.loads(data)))
                self.logger.info(json_func.dumps(json_func.loads(data), ensure_ascii=False, indent=2))
            except BaseException:
                self.logger.info(pformat(data))

        if json is not None:
            self.logger.info("JSON: " + os.linesep + json_func.dumps(json, ensure_ascii=False, indent=2))

        if len(kwargs.keys()) > 0:
            self.logger.info("kwargs:" + os.linesep + json_func.dumps(kwargs, ensure_ascii=False, indent=2))

        response = requests.post(url, data, json, **kwargs)

        self.logger.info("<<<<<<<< POST Response: ")
        self.logger.info(response)

        if response.status_code == 200:
            try:
                # dumps()方法中的 indent参数 如果 不为空 则会自动format输出结果
                self.logger.info(os.linesep + json_func.dumps(response.json(), ensure_ascii=False, indent=2))
            except BaseException:
                self.logger.info(response.__dict__)
                return response

        self.logger.info("========================= POST Request Completed =========================" + os.linesep)

        return response

    @log_curl
    def put(self, url, data=None, **kwargs):
        if hasattr(settings, "auto_log_request") and settings.auto_log_request is False:
            return requests.put(url, data, **kwargs)

        self.logger.info("========================= PUT Request Start =========================" + os.linesep)
        self.logger.info("URL: " + url)

        if data is not None:
            try:
                self.logger.info("data: " + os.linesep + pformat(json_func.loads(data)))
            except BaseException:
                self.logger.info(os.linesep + pformat(data))

        if len(kwargs.keys()) > 0:
            self.logger.info("kwargs: " + os.linesep + json_func.dumps(kwargs, ensure_ascii=False, indent=2))

        response = requests.put(url, data, **kwargs)

        self.logger.info("<<<<<<<< PUT Response:")
        self.logger.info(response)

        if response.status_code == 200:
            try:
                self.logger.info(os.linesep + json_func.dumps(response.json(), ensure_ascii=False, indent=2))
            except BaseException:
                return response

        self.logger.info("========================= PUT Request Completed =========================" + os.linesep)

        return response

    @log_curl
    def delete(self, url, **kwargs):
        if hasattr(settings, "auto_log_request") and settings.auto_log_request is False:
            return requests.delete(url, **kwargs)

        self.logger.info("========================= DELETE Request Start =========================" + os.linesep)
        self.logger.info("URL: " + url)

        if len(kwargs.keys()) > 0:
            self.logger.info("kwargs: " + os.linesep + json_func.dumps(kwargs, ensure_ascii=False, indent=2))

        response = requests.delete(url, **kwargs)

        self.logger.info("<<<<<<<< DELETE Response:")
        self.logger.info(response)

        if response.status_code == 200:
            try:
                self.logger.info(os.linesep + json_func.dumps(response.json(), ensure_ascii=False, indent=2))
            except BaseException:
                return response

        self.logger.info("========================= DELETE Request Completed =========================" + os.linesep)

        return response
