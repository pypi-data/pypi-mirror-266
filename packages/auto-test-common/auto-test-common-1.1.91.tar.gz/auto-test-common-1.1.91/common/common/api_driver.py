import requests
from common.autotest.handle_allure import allure_api_step
from requests_toolbelt import MultipartEncoder
from os import path
import os
from common.config.config import TEST_FILE_PATH


class APIDriver(object):

    session = None

    @classmethod
    def get_session(cls):
        if cls.session is None:
            cls.session = requests.Session()
        return cls.session

    @classmethod
    def http_request(cls, url, method, parametric_key=None, header=None, data=None, file=None, cookie=None, _auth=None,
                     desc: str="") -> object:
        """
        :param method: 请求方法
        :param url: 请求url
        :param parametric_key: 入参关键字， params(查询参数类型，明文传输，一般在url?参数名=参数值), data(一般用于form表单类型参数)
        json(一般用于json类型请求参数)
        :param data: 参数数据，默认等于None
        :param file: 文件对象
        :param desc: 自动化测试过程请求描述：打印到Report中
        :param header: 请求头
        :return: 返回res对象
        """
        session = cls.get_session()
        if parametric_key is None:
            header = cls.getCommontHeader(header)
            res = session.request(method=method, url=url, headers=header, cookies=cookie,
                                  auth=_auth,verify=False)
            allure_api_step(desc, url, method, header, '', '', res)

        elif parametric_key == 'params':
            header = cls.getCommontHeader(header)
            res = session.request(method=method, url=url, params=data, headers=header, cookies=cookie,
                                  auth=_auth,verify=False)
            allure_api_step(desc, url, method, header, data, '', res)

        elif parametric_key == 'data':
            header = cls.getCommontHeader(header)
            res = session.request(method=method, url=url, data=data, files=file, headers=header, cookies=cookie,
                                  auth=_auth,verify=False)
            allure_api_step(desc, url, method, header, data, file, res)

        elif parametric_key == 'text':
            header = cls.getCommontHeader(header)
            header['Content-Type'] = 'text/plain'
            res = session.request(method=method, url=url, data=data, files=file, headers=header, cookies=cookie,
                                  auth=_auth, verify=False)
            allure_api_step(desc, url, method, header, data, file, res)

        elif parametric_key == 'json':
            header = cls.getCommontHeader(header)
            header['Content-Type'] = 'application/json'
            res = session.request(method=method, url=url, json=data, files=file, headers=header, cookies=cookie,
                                  auth=_auth,verify=False)
            allure_api_step(desc, url, method, header, data, file, res)

        elif parametric_key == 'xml':
            header = cls.getCommontHeader(header)
            header['Content-Type'] = 'application/xml'
            res = session.request(method=method, url=url, data=data, files=file, headers=header, cookies=cookie,
                                  auth=_auth, verify=False)
            allure_api_step(desc, url, method, header, data, file, res)

        elif parametric_key == 'form':
            header = cls.getCommontHeader(header)
            header['Content-Type'] = 'application/x-www-form-urlencoded'
            try:
                if isinstance(data, str):
                    from common.data.data_process import DataProcess
                    data = DataProcess.handle_data(data)
            except Exception as e:
                logger.info(f'测试数据：{data} 转换异常:' + repr(e))
            res = session.request(method=method, url=url, data=data, files=file, headers=header, cookies=cookie,
                                  auth=_auth, verify=False)
            allure_api_step(desc, url, method, header, data, file, res)

        elif parametric_key == 'form-data':
            if data is not None:
                data = cls.handleFile(data)
                m = MultipartEncoder(data)
                header = cls.getCommontHeader(header)
                header['Content-Type'] = m.content_type
                res = session.request(method=method, url=url, data=m, headers=header, cookies=cookie,
                                      auth=_auth, verify=False)
                allure_api_step(desc, url, method, header, data, file, res)
        else:
            raise ValueError('可选关键字为params, data, xml, json, text, form,form-urlencoded')
        session.close()
        return res

    @classmethod
    def getCommontHeader(self, header):
        if header is None:
            header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/83.0.4103.116 Safari/537.36',
                      'Connection':'keep-alive',
                      'Accept-Encoding':'gzip, deflate, br',
                      'Accept-Language':'zh-CN,zh;q=0.9',
                      'Accept':'*/*'}
        else:
            if 'User-Agent' not in header:
                header['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/83.0.4103.116 Safari/537.36'
            if 'Connection' not in header:
                header['Connection'] = 'keep-alive'
            if 'Accept-Encoding' not in header:
                header['Accept-Encoding'] = 'gzip, deflate, br'
            if 'Accept-Language' not in header:
                header['Accept-Language'] = 'zh-CN,zh;q=0.9'
            if 'Accept' not in header:
                header['Accept'] = '*/*'
        return header

    @classmethod
    def handleFile(self,data):
        if isinstance(data,dict):
            for key in data:
                if isinstance(data[key], str):
                    if os.path.exists(path.join(TEST_FILE_PATH, data[key])):
                        all_path = os.sep.join([TEST_FILE_PATH, data[key]])
                        from common.file.handle_system import adjust_path
                        all_path = adjust_path(all_path)
                        data[key] = (data[key], open(all_path, 'rb'))
                elif isinstance(data[key], tuple):
                    if os.path.exists(path.join(TEST_FILE_PATH, data[key][1])):
                        if data[key].__len__() == 3:
                            all_path = os.sep.join([TEST_FILE_PATH, data[key][1]])
                            from common.file.handle_system import adjust_path
                            all_path = adjust_path(all_path)
                            data[key] = (data[key][0], open(all_path, 'rb'), data[key][2])
                        elif data[key].__len__() == 2:
                            all_path = os.sep.join([TEST_FILE_PATH, data[key][1]])
                            from common.file.handle_system import adjust_path
                            all_path = adjust_path(all_path)
                            data[key] = (data[key][0], open(all_path, 'rb'))
                else:
                    data = data
        return data



