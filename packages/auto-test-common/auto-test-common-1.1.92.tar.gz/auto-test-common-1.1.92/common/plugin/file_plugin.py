import base64
import json
from os import path
from common.data.handle_common import get_system_key,set_system_key
from lxml import etree
from loguru import logger
from common.common.constant import Constant
from common.plugin.data_plugin import DataPlugin
from common.db.handle_db import MysqlDB
from common.data.data_process import DataProcess
from common.file.ReadFile import ReadFile
from common.plugin.data_bus import DataBus
from common.config.config import TEST_DATA_PATH
from common.file.handle_excel import excel_to_list,write_to_excel



class FilePlugin(object):

    @classmethod
    def load_data(self, fileName, data=None):
        content = f'{fileName}文件内容不存在'
        try:
            if fileName.find(".json") >= 0:
                content = self.load_json(fileName, _dict=data)
            elif fileName.find(".xml") >= 0:
                content = self.load_xml(fileName, _dict=data)
            elif fileName.find(".txt") >= 0:
                content = self.load_xml(fileName, _dict=data)
            elif fileName.find(".yaml") >= 0:
                if fileName.find(".yaml|") >= 0:
                    from common.plugin.yaml_plugin import YamlPlugin
                    _arr = fileName.split('|')
                    content = YamlPlugin.load_data(_arr[0], _arr[1])
                else:
                    from common.plugin.yaml_plugin import YamlPlugin
                    content = YamlPlugin.load_data(fileName)
        except Exception as e:
            logger.info(f'{fileName}文件内容不存在')
        return content


    @classmethod
    def excel_to_dict(self, file_name, sheet: str='Sheet1', _filter: dict=None, _index:int=1, _replace: bool=True, file_path: str=TEST_DATA_PATH):
        """
           读取Excel中特定sheet的数据，按行将数据存入数组datalist[从第二行开始读数据】
           :param data_file:Excel文件目录
           :param sheet:需要读取的sheet名称
           :return:datalist
           """
        _list = []
        DataBus.save_init_data()
        file_name_temp = path.join(file_path, file_name)
        if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() == '脚本同步':
            excel_sheet = file_name_temp + "_" + sheet
            if DataProcess.isNotNull(get_system_key(Constant.SYNC_EXCEL_SHEET)):
                if get_system_key(Constant.SYNC_EXCEL_SHEET).find(excel_sheet.strip()+";") < 0:
                    sync_excel_sheet = get_system_key(Constant.SYNC_EXCEL_SHEET) + ";" + excel_sheet.strip()+";"
                    logger.info(f"文件路径:{file_name_temp} Sheet:{sheet} 脚本用例文件开始同步")
                    set_system_key(Constant.SYNC_EXCEL_SHEET, sync_excel_sheet, True)
                    _list = excel_to_list(file_name_temp, sheet, _index)
                else:
                    logger.info(f"文件路径:{file_name_temp} Sheet:{sheet} 脚本用例文已经被处理")
            else:
                set_system_key(Constant.SYNC_EXCEL_SHEET,excel_sheet.strip()+";")
                logger.info(f"文件路径:{file_name_temp} Sheet:{sheet} 脚本用例文件开始同步")
                _list = excel_to_list(file_name_temp, sheet, _index)
        else:
            _list = excel_to_list(file_name_temp, sheet, _index, _filter,  _replace, _checkData=True)
            _list = DataProcess.list_dict_duplicate_removal_byKey(_list, Constant.CASE_TITLE)
            _list = DataProcess.list_dict_duplicate_removal_byKey(_list, Constant.CASE_NO)
            for _temp in _list:
                for key in _temp.keys():
                    _fileName, _sheet, _filter = self.handle_excel_data(_temp[key],file_name,sheet)
                    if DataProcess.isNotNull(_fileName):
                        _subData = excel_to_list(path.join(file_path, _fileName), _sheet, _index, _filter, _replace, _checkData=False)
                        if _subData.__len__() > 0:
                            _temp[key] = _subData[0]
                            _temp["$"+key] = _subData
        return _list

    @classmethod
    def handle_excel_data(self, _str:str, _fileName:str, _sheetName:str):
        """
        处理Excel数据格式$[excel文件名称.SheetName.fileter==1]
        """
        if isinstance(_str, str) and _str.find('$[') >= 0:
            _str = _str.replace('$[',"").replace(']',"")
            _arr = _str.split('==')
            _sub= _arr[0].split('.')
            if _sub.__len__() == 3:
                _fileName = _sub[0]
                _sheetName = _sub[1]
                _fileter = {_sub[2]:_arr[1]}
            if  _sub.__len__() == 2:
                _fileName = _fileName
                _sheetName = _sub[0]
                _fileter = {_sub[1]:_arr[1]}
            if _sub.__len__() == 1:
                _fileName = _fileName
                _sheetName = _sheetName
                _fileter = {_sub[0]:_arr[1]}
            return _fileName,_sheetName,_fileter
        else:
            return "","",""


    @classmethod
    def write_case_data(self, item: dict, key, value):
        """
         回填测试数据到Excel中
                   :param data_file:Excel文件目录
                   :param sheet:需要读取的sheet名称
                   :return:datalist
                   """
        _cell = item.get(key+'_cell')
        write_to_excel(item.get('_excelPath'), item.get('_sheetName'), _cell['row'], _cell['col'], value)


    @classmethod
    def excel_to_list(cls, testData_path, sheet_name: str = '', _replace: bool=True):
        """
        读取excel格式的测试用例,转换成list
        :return: data_list - pytest参数化可用的数据
        """
        DataBus.save_init_data()
        if _replace:
            _data = DataBus.get_data(ReadFile.get_testcase(testData_path, sheet_name))
        else:
            _data = ReadFile.get_testcase(testData_path, sheet_name)
        return _data

    @classmethod
    def get_all_data(cls, testData_path, sheet_name: str = '', _replace: bool = True):
        """
        获取所以Excel数据并转换为List
        :return: data_list - pytest参数化可用的数据
        """
        DataBus.save_init_data()
        if _replace:
            return DataBus.get_data(ReadFile.get_all_data(testData_path, sheet_name))
        else:
            return ReadFile.get_all_data(testData_path, sheet_name)



    @classmethod
    def load_json(self, file_name, _dict=None, _replace: bool=True, file_path: str=TEST_DATA_PATH, _no_content =0, _remove_null:bool=False):
        """
        把Json模版转换为JSON数据,默认找不到数据用空代替
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        DataBus.save_init_data()
        _path = path.join(file_path, file_name,)
        with open(_path, "rb") as json_file:
            _json = json.load(json_file)
        _json = DataPlugin.checkData(_json, _dict, _replace, _no_content, _remove_null)
        return _json

    @classmethod
    def check_data(self,testData:list):
        return DataProcess.check_test_data(testData)

    @classmethod
    def load_file(self, file_name, _dict=None, _replace: bool = True, file_path: str = TEST_DATA_PATH, _no_content=0,
                  _remove_null: bool = False,_readMode=1):
        """
        把Json模版转换为JSON数据,默认找不到数据用空代替
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :param _readMode (0：一行一行读成list，1：全部一起读出）
        :return:
        """
        DataBus.save_init_data()
        _list=[]
        _path = path.join(file_path, file_name, )
        with open(_path, "r", encoding='utf-8') as _file:
            if _readMode == 0:
                _datas =_file.readlines()
                for _data in _datas:
                    _data = DataPlugin.checkData(_data, _dict, _replace, _no_content, _remove_null)
                    _list.append(_data)
            if _readMode == 1:
                _list = _file.read()
                _list = DataPlugin.checkData(_list, _dict, _replace, _no_content, _remove_null)
        return _list

    @classmethod
    def load_xml(self, file_name, _xpath, _dict=None, _replace: bool = True, file_path: str = TEST_DATA_PATH, _no_content=0,
                  _remove_null: bool = False):
        """
        加载xml数据
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        DataBus.save_init_data()
        _path = path.join(file_path, file_name, )
        _tree = etree.parse(_path)
        for bbox in _tree.xpath(_xpath):  # 获取bndbox元素的内容
            if len(bbox.getchildren())>0:
                for corner in bbox.getchildren():  # 便利bndbox元素下的子元素
                    _xml = corner.text  # string类型
            else:
                _xml = bbox.text
        _data = DataPlugin.checkData(_xml, _dict, _replace, _no_content, _remove_null)
        return _data

    @classmethod
    def write_file(self,content,file):
        """
        把请求数据写入文件
        :param content:
        :param file:
        :return:
        """
        DataProcess.write_file(file,content)

    @classmethod
    def load_more_json(self, file_name, _dict=None, _remove_null:bool=False, file_path: str=TEST_DATA_PATH,):
        """
        把Json模版转换为JSON数据,默认找不到数据用空代替
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        DataBus.save_init_data()
        _path = path.join(file_path, file_name,)

    @classmethod
    def image_convert_base64(self, file_name, file_path: str=TEST_DATA_PATH):
        _path = path.join(file_path, file_name, )
        f = open(_path, 'rb')  # 二进制方式打开图文件
        ls_f = base64.b64encode(f.read())  # 读取文件内容，转换为base64编码
        f.close()
        return ls_f



    @classmethod
    def mysql_load_list_dict(self, _sql=None, _config=None):
        """
        把数据库中的表作为dict
        :return:
        """
        if _config is None:
            _config = {'key': 'atf'}
        _mysql = MysqlDB(_config)
        _list = _mysql.execute(_sql).fetchall()
        _mysql.close()
        return _list

    @classmethod
    def mysql_load_dict(self, _sql=None, _config=None):
        """
        把数据库中的表作为dict
        """
        if _config is None:
            _config = {'key': 'atf'}
        _mysql = MysqlDB(_config)
        _list = _mysql.execute(_sql).fetchone()
        _mysql.close()
        return _list

    @classmethod
    def _dict_contain(self,_data,_temp:list):
        _flag = True
        self._get_jenkin_TestCaseMark(_data)
        for i, j in _data.items():
            if i in _temp.keys():
                if j != str(DataProcess.get_key_dic(_temp, i)).strip():
                    _flag = False
        _flag = self._get_jenkin_TestCaseName(_temp,_flag)
        return _flag

    @classmethod
    def _get_jenkin_TestCaseMark(self,_dict):
        if get_system_key('TestCaseMark') is not None and get_system_key('TestCaseMark').strip() !='':
            _mark=get_system_key('TestCaseMark')
            if _mark.find(";")!=-1:
                _arr=_mark.split(';')
                for _temp in _arr:
                    _tempKey=_temp.split('&')
                    _dict[_tempKey[0]]=_dict[1]
            else:
                _dict[Constant.CASE_PRIORITY]=get_system_key('TestCaseMark')
        return _dict

    @classmethod
    def _get_jenkin_TestCaseName(self,_dict,_flag):
        if get_system_key(Constant.TEST_CASE_NAME_LIST) is not None and get_system_key(Constant.TEST_CASE_NAME_LIST).strip() !='':
            _mark = eval(get_system_key(Constant.TEST_CASE_NAME_LIST))
            if _dict[Constant.CASE_TITLE] in _mark:
                _flag = True
            else:
                _flag = False
        return _flag



if __name__ == '__main__':
    str = 'test/test_single/test_emgRe_pi_bum_user.py::TestBumDept::test_bumUserAdd[testdata20]'
    _str =str[0:str.find('[')]
    print(_str)
















