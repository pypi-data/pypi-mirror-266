import json
from typing import Iterable
from common.plugin.data_bus import DataBus
import xmltodict
from common.data.data_process import DataProcess
from common.data.handle_common import req_expr, convert_json, extractor
from common.data.handle_common import get_system_key


class DataPlugin(object):

    @classmethod
    def datetime_utc_to_local(self, utc_datetime):
        """
        时间从UTC转换Local
        """
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        return parser.parse(utc_datetime) + offset


    @classmethod
    def convert_json(self, _temp, _replace: bool = True):
        """
        任意的数据类型转换成Json
        :param _temp:
        :param _replace: 是否清洗数据
        :return:
        """
        content = _temp
        if isinstance(_temp, str):
            content = json.loads(content)
        else:
            content = json.dumps(_temp,ensure_ascii=False)
        if _replace:
            content = req_expr(content)
        return content

    @classmethod
    def json_convert_dict(self, _json, _replace: bool = True) -> dict:
        """
              Json字符串转换为字典
              :param _json:
              :param _replace: 是否清洗数据
              :return:
              """
        if _replace:
            _json = req_expr(_json)
        return convert_json(_json)

    @classmethod
    def xml_convert_dict(self,_xml, _replace: bool = True):
        """
                     XML字符串转换为字典
                     :param _xml:
                     :param _replace: 是否清洗数据
                     :return:
                     """
        if _replace:
            _xml = req_expr(_xml)
        return xmltodict.parse(_xml)

    @classmethod
    def dict_convert_xml(self,_dict, _replace: bool = True):
        """
                     字典转换成XML
                     :param _xml:
                     :param _replace: 是否清洗数据
                     :return:
                     """
        if _replace:
            _dict = DataProcess.handle_data_fromat(_dict)
        return xmltodict.unparse(_dict)

    @classmethod
    def get_key_dic(self,_data, key):
        return DataProcess.get_key_dic(_data,key)


    @classmethod
    def get_data_jpath(self, obj: dict, expr: str = '.', error_flag: bool = False):
        """
            通过Jpath获取json数据
        :param obj:
        :param expr:
        :param error_flag:
        :return:
        """
        return extractor(obj, expr, error_flag)

    @classmethod
    def load_json_object(self,_json):
        newObj = dict()
        DataProcess.parseJson(_json, newObj)
        return self.del_dict_no_content(newObj)

    @classmethod
    def load_json_data(self, _json, _dict=None, _replace: bool=True, _no_content =0, _remove_null:bool=False):
        DataBus.save_init_data()
        if _remove_null:
            if _replace:
                _json = DataBus.get_data(_json, _dict, 2)
            _json = DataPlugin.remove_empty(_json)
        else:
            if _replace:
                _json = DataBus.get_data(_json, _dict, _no_content)
        return _json


    @classmethod
    def _json_empty(self, _item):
        if isinstance(_item, Iterable):
            return not _item
        elif isinstance(_item, str):
            return _item == ''
        else:
            return False

    @classmethod
    def remove_empty(self,item):
        if isinstance(item, dict):
            new_item = {k: self.remove_empty(v) for k, v in item.items()}
            return {k: v for k, v in new_item.items() if not self._json_empty(v)}
        elif isinstance(item, (list, tuple)):
            new_item = [self.remove_empty(v) for v in item]
            return [v for v in new_item if not self._json_empty(v)]
        else:
            return item

    @classmethod
    def get_date(self, now):
       return DataProcess.getDate(now)

    @classmethod
    def isNotNull(self, data):
        return DataProcess.isNotNull(data)

    @classmethod
    def checkData(self, data, dict: dict = None, _replace: bool = True, _no_content=0, _remove_null: bool = False,):
        if _remove_null:
            if _replace:
                data = DataBus.get_data(data, dict, 2)
            data = DataPlugin.remove_empty(data)
        else:
            if _replace:
                data = DataBus.get_data(data, dict, _no_content)
        return data

    @classmethod
    def checkScriptSync(self):
        """
        判断是否是脚本同步
        """
        if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() == '脚本同步':
            return True
        else:
            return False

    @classmethod
    def list_dict_duplicate_removal(self,list_dict):
        """列表中字典去重"""
        return DataProcess.list_dict_duplicate_removal(list_dict)

    @classmethod
    def list_dict_duplicate_removal_byKey(self, list_dict, key):
        """列表中嵌套字典，按字典中得某个键去重"""
        return DataProcess.list_dict_duplicate_removal_byKey(list_dict, key)

    @classmethod
    def check_test_data(self, testdatas:list):
        """
        检查list中的数据是否合法
        """
        return DataProcess.check_test_data(testdatas)

















