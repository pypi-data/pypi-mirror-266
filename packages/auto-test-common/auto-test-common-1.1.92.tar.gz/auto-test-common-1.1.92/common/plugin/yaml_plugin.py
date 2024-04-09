from os import path
from common.plugin.data_plugin import DataPlugin
from common.config.config import TEST_DATA_PATH
from common.file.handle_yaml import get_yaml_dict,get_yaml_data
from common.data.data_process import DataProcess
from common.common.constant import Constant
from common.plugin.data_bus import DataBus
from common.data.handle_common import print_debug

class YamlPlugin(object):

    @classmethod
    def load_data(self,file_name,file_path: str = TEST_DATA_PATH):
        DataBus.save_init_data()
        _path = path.join(file_path, file_name, )
        yamlData = get_yaml_data(_path)
        return yamlData

    @classmethod
    def get_dict(self,file_name, key:str=None, file_path: str = TEST_DATA_PATH):
        DataBus.save_init_data()
        file_name = path.join(file_path, file_name, )
        yamlData = get_yaml_dict(file_name, key)
        return yamlData

    @classmethod
    def get_data(self,file_name,  dict: dict = None, _replace: bool=True, file_path: str = TEST_DATA_PATH,_remove_null:bool=False,_no_content =0) -> "list":
        DataBus.save_init_data()
        file_name = path.join(file_path, file_name, )
        yamlData = self.get_dict(file_name)
        datas = DataProcess.check_test_data(yamlData)
        datas = DataProcess.list_dict_duplicate_removal_byKey(datas, Constant.CASE_TITLE)
        datas = DataProcess.list_dict_duplicate_removal_byKey(datas, Constant.CASE_NO)
        _datas = []
        for _temp in datas:
            _data = {}
            for key in _temp.keys():
                _data[key] = DataPlugin.checkData(_temp[key], dict, _replace, _remove_null, _no_content)
                if key == Constant.TEST_DATA:
                    for _key in _data[Constant.TEST_DATA].keys():
                        _data[_key] = DataPlugin.checkData(_data[Constant.TEST_DATA][_key], dict, _replace, _remove_null, _no_content)
            _datas.append(_data)
        print_debug("最终参数化测试数据:"+str(_datas))
        return _datas



if __name__ == '__main__':
    str="aa:${aa.json}"
    print(DataBus.get_data(str))


