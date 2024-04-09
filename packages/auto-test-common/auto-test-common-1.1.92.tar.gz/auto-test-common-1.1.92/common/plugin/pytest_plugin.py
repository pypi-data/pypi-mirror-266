# -*- coding: utf-8 -*-
import json
import os
import pytest
from _pytest.nodes import Item
from common.db.handle_db import MysqlDB
from loguru import logger
from common.plat.jira_platform import JiraPlatForm
from common.config.config import LOG_PATH_FILE, TEST_PATH, TEST_TARGET_RESULTS_PATH, TEST_TARGET_REPORT_PATH,TEST_UI_PATH
from common.data.handle_common import get_system_key,format_caseName,print_info,set_system_key,print_debug
from common.plat.mysql_platform import MysqlPlatForm
from common.file.handle_system import del_file
from common.common.constant import Constant
from common.data.data_process import DataProcess
from common.plugin.data_bus import DataBus
from common.plat.ATF_platform import ATFPlatForm
from common.plat.service_platform import ServicePlatForm
from common.plugin.atf_plugin import ATFPlugin
from common.autotest.handle_allure import allure_title,allure_testcase_link,allure_severity
from os import path


class PytestPlugin(object):

    @classmethod
    def getCaseNameList(self):
        """
        获取用例列表
        """
        case_name_list = []
        if DataProcess.isNotNull(get_system_key('Result')):
            case_name_list = ATFPlatForm.getCycleByResult(get_system_key('Result'))
        else:
            case_name_list = ATFPlatForm.getCycleByResult()
        PytestPlugin.initRunCyleCase()
        case_name_list_str =""
        for temp in case_name_list:
            case_name_list_str = case_name_list_str+ temp['casename']+";"
        logger.info("获取需要执行的测试用例:"+case_name_list_str)
        return case_name_list



    @classmethod
    def insertCaseToPlan(self):
        if DataProcess.isNotNull(get_system_key('addCaseJql')) and DataProcess.isNotNull(get_system_key(Constant.ISSUE_KEY)):
            JiraPlatForm.saveCaseToTestPlanByJql(get_system_key('issueKey'),get_system_key('addCaseJql'))


    @classmethod
    def runPathCase(self, _path):
        _pathlist = _path.split(',')
        for _path in _pathlist:
            case_path = os.path.join(TEST_PATH, _path)
            logger.info("开始执行脚本的路径:" + case_path)
            if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() == '脚本同步':
                pytest.main(
                    args=['-vs', '-n=10', case_path,
                          f'--alluredir={TEST_TARGET_RESULTS_PATH}'])
            else:
                if DataProcess.isNotNull(get_system_key(Constant.TEST_RUN_THREAD)):
                    thread = get_system_key(Constant.TEST_RUN_THREAD).strip()
                    pytest.main(
                        args=['-vs', f'-n={thread}', case_path,
                              f'--alluredir={TEST_TARGET_RESULTS_PATH}'])
                else:
                    pytest.main(
                        args=['-vs', case_path,
                              f'--alluredir={TEST_TARGET_RESULTS_PATH}'])
            logger.info("执行脚本成功:" + case_path)

    @classmethod
    def runCaseByTitle(self, caseName):
        _list = []
        _config = {'key': 'atf'}
        _mysql = MysqlDB(_config)
        _gitName = get_system_key(Constant.GIT_PROJECTNAME)
        _sql = f"select distinct(caseurl) from test_autotest_script where  " \
               f"test_autotest_script.testname ='{caseName}' and gitname='{_gitName}'"
        _list = _mysql.execute(_sql).fetchall()
        _mysql.close()
        for caseName in _list:
            caseUrl = str(caseName['caseurl']).replace("(", "").replace(")", "")
            _scriptPath = path.join(get_system_key(Constant.CURRENT_PATH), caseUrl, )
            logger.info(f"---------执行参数化脚本路径:{_scriptPath}-------------")
            pytest.main(
                args=['-vs', _scriptPath,
                        f'--alluredir={TEST_TARGET_RESULTS_PATH}'])
            logger.info("----------执行脚本成功---------------")

    @classmethod
    def runSceneCase(self, _caseNameList):
        _list = []
        _scriptPathlist = ""
        thread = int(DataBus.get_key(Constant.TEST_RUN_THREAD).strip())
        logger.info('去重前脚本数:'+str(_caseNameList.__len__()))
        _listscript = list(map(lambda x: x['script'], _caseNameList))
        _listscript.sort()
        logger.info('去重前脚本信息:' + str(_listscript))
        _caseNameList = DataProcess.list_script_removal_byKey(_caseNameList, 'script')
        logger.info('去重后脚本数:' + str(_caseNameList.__len__()))
        _listscript = list(map(lambda x: x['script'].split('[')[0], _caseNameList))
        _listscript.sort()
        logger.info('去重后脚本信息:'+ str(_listscript))
        for case in _caseNameList:
            _list = ATFPlatForm.getCaseRun(case['caseid'])
            caseId = _list['caseid']
            caseStatus = _list['status']
            scriptURL= _list['script']
            if caseStatus == Constant.STATUS_PRE or caseStatus == Constant.STATUS_AUTOTEST_PARA:
                if scriptURL != '':
                    caseUrl = str(scriptURL).replace("(", "").replace(")", "")
                    _scriptPath = path.join(get_system_key(Constant.CURRENT_PATH), caseUrl.split('[')[0], )
                    ServicePlatForm.updateByRunid(_list['caserunid'], Constant.STATUS_AUTOTEST, "")
                    if thread > 1:
                        if _scriptPathlist.find(_scriptPath) < 0:
                            logger.info(f"------用例信息:{str(_list)}  脚本路径:{_scriptPath}  加入多线程执行列表-------")
                            _scriptPathlist = _scriptPathlist + _scriptPath + ","
                    else:
                        logger.info(f"------用例信息:{str(_list)}  脚本路径:{_scriptPath}  准备执行-------")
                        pytest.main(
                            args=['-vs', _scriptPath, f'--alluredir={TEST_TARGET_RESULTS_PATH}'])
                else:
                    logger.info(f"-------用例信息:{str(_list)}  未关联脚本【无需执行】------")
                    MysqlPlatForm.delete_autotest_script(caseId)
            else:
                logger.info(f"------用例信息:{str(_list)}  执行完成-------")
        if DataProcess.isNotNull(_scriptPathlist):
            logger.info(f"脚本路径列表:{_scriptPathlist}  准备执行-------")
            pytest.main(
                args=['-vs',f'-n={thread}', _scriptPathlist, f'--alluredir={TEST_TARGET_RESULTS_PATH}'])

    @classmethod
    def initRunCyleCase(self):
        if DataProcess.isNotNull(get_system_key(Constant.TEST_SRTCYCLE_ID)):
            ServicePlatForm.updateStausByCycleId(get_system_key(Constant.TEST_SRTCYCLE_ID), Constant.STATUS_PRE)

    @classmethod
    def pytest_run_case(cls, _deleteResult:bool= True):
        """
        运行自动化用例
        :return:
        """
        if DataProcess.isNotNull(get_system_key('addCaseJql')) and DataProcess.isNotNull(
                get_system_key(Constant.ISSUE_KEY)):
            JiraPlatForm.saveCaseToTestPlanByJql(get_system_key(Constant.ISSUE_KEY), get_system_key('addCaseJql'))
        else:
            DataBus.save_init_data()
            if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() == '脚本同步':
                MysqlPlatForm.delete_autotest_script_byGitName(get_system_key('gitProjectName'))
            if DataProcess.isNotNull(get_system_key(Constant.TEST_SRTCYCLE_ID)):
                ATFPlatForm.syncCycleNameCase()
            DataBus.run_info()
            logger.add(LOG_PATH_FILE, enqueue=True, encoding='utf-8')
            if _deleteResult:
                del_file(TEST_TARGET_RESULTS_PATH)
            if DataProcess.isNotNull(get_system_key(Constant.TEST_SRTCYCLE_ID)):
                ServicePlatForm.updateCaseRun(get_system_key(Constant.TEST_SRTCYCLE_ID),Constant.STATUS_AUTOTEST, '0.0%', "running")
                _caseNameList = PytestPlugin.getCaseNameList()
                if len(_caseNameList) == 0:
                    logger.info("无测试用例列表可运行")
                else:
                    PytestPlugin.runSceneCase(_caseNameList)
            else:
                logger.info("运行测试文件:" + get_system_key(Constant.TEST_CASE_PATH))
                PytestPlugin.runPathCase(get_system_key(Constant.TEST_CASE_PATH))
            if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() == '脚本同步':
                ServicePlatForm.syncJiraCaseAndBug()

    @classmethod
    def allure_report(cls):
        """
        生成测试报告
        :return:
        """

        if get_system_key(Constant.ALLURE_PATH) is not None:
            ALLURE_PATH = get_system_key(Constant.ALLURE_PATH)
        else:
            ALLURE_PATH = ''
        if DataProcess.isNotNull(get_system_key(Constant.RUN_TYPE)) == False:
            os.system(f'{ALLURE_PATH}allure generate {TEST_TARGET_RESULTS_PATH} -o {TEST_TARGET_REPORT_PATH} --clean')
            logger.success('Allure测试报告已生成')
        # ATFPlugin.sendResult()

    @classmethod
    def change_allure_title(cls,report_html_path: str = TEST_TARGET_REPORT_PATH):
        """
        修改Allure标题
        :param name: 
        :param report_html_path: 
        :return: 
        """
        dict = {}
        DataBus.save_init_data()
        # 定义为只读模型，并定义名称为f
        with open(f'{report_html_path}/widgets/summary.json', 'rb') as f:
            # 加载json文件中的内容给params
            params = json.load(f)
            # 修改内容
            params['reportName'] = get_system_key("JOB_NAME")
            # 将修改后的内容保存在dict中
            dict = params
            logger.info("修改测试报告名称：" + get_system_key(Constant.PROJECT_NAME))
            with open(f'{report_html_path}/widgets/summary.json', 'w', encoding="utf-8") as r:
                # 将dict写入名称为r的文件中
                json.dump(dict, r, ensure_ascii=False, indent=4)

            # 关闭json读模式
            f.close()
            logger.info("修改测试报告完成")

    @classmethod
    def sendReport(self):
        DataBus.save_init_data()
        change_allure_title()
        ATFPlugin.sendResult()

    @classmethod
    def generated_code(self, _url: str = '', _path: str = TEST_UI_PATH):
        if not DataProcess.isNotNull(_url):
            _url = get_system_key('url')
        test_case_dir = '{}'.format(_path)
        file_list = [os.path.join(test_case_dir, file) for file in os.listdir(test_case_dir) if "test_" in file]
        test_case_num = len(file_list) - 2
        print("{}目录下存在{}测试用例".format(test_case_dir, test_case_num))
        cmd = r"python -m playwright codegen --target pytest -o {}/test_{}.py -b chromium {}". \
            format(_path, str(test_case_num + 1).zfill(3), _url)
        print("执行录制测试用例命令：{}".format(cmd))
        os.system(cmd)

    @classmethod
    def pytest_case_meta(self, item: Item):
        DataBus.save_init_data()
        _caseTitle, _caseNo = PytestPlugin.getCaseName(item)
        PytestPlugin.jira_convert_allure(_caseTitle, _caseNo)
        PytestPlugin.sync_case_Script(item, _caseTitle, _caseNo)
        PytestPlugin.send_case_result(item, Constant.STATUS_AUTOTEST)

    @classmethod
    def getCaseName(self, item: Item):
        _caseTitle = "脚本未设置用例名称"
        _caseNo = "00000"
        _caseData = ""
        try:
            parmkes = item._pyfuncitem.callspec.indices.keys()
            if DataProcess.isNotNull(parmkes):
                _caseTitle = item._pyfuncitem.callspec.params[list(parmkes)[0]].get(Constant.CASE_TITLE)
                _caseNo = item._pyfuncitem.callspec.params[list(parmkes)[0]].get(Constant.CASE_NO)
                _caseData = item._pyfuncitem.callspec.params[list(parmkes)[0]]
        except Exception as e:
            print_info('未通过Excel获取到用例信息')
        try:
            temp = item.__dict__['keywords'].__dict__['_markers']['__allure_display_name__']
            if temp != Constant.TEST_DATA_PARAMETER:
                _caseTitle = temp
        except Exception as e:
            print_info('未通过装饰器title获取到用例信息')
        try:
            if _caseTitle == "脚本未设置用例名称":
                temp = item.__dict__['keywords']._markers['__allure_display_name__']
                if temp != Constant.TEST_DATA_PARAMETER:
                    _caseTitle = temp
        except Exception as e:
            print_info('第二次未通过装饰器title获取到用例信息')
        try:
            if _caseNo == '00000' or _caseNo is None:
                _args = item.__dict__['keywords'].__dict__['_markers']['pytestmark']
                for arg in _args:
                     label_type = arg.__dict__['kwargs']['label_type']
                     if label_type == 'as_id':
                         _caseNo = arg.__dict__['args'][0]
        except Exception as e:
            print_info('未通过装饰器ID获取到用例信息')
        try:
            if _caseNo == '00000' or _caseNo is None:
                _args = item.__dict__['keywords']._markers['pytestmark']
                for arg in _args:
                    label_type = arg.__dict__['kwargs']['label_type']
                    if label_type == 'as_id':
                        _caseNo = arg.__dict__['args'][0]
        except Exception as e:
            print_info('第二次未通过装饰器ID获取到用例信息')
        print_info(f"执行用例名称:{_caseTitle} 用例编号:{_caseNo}")
        print_info(f'用例数据:{_caseData}')
        return _caseTitle, _caseNo

    @classmethod
    def send_result(self, item: Item, report):
        print_debug("send_result: Item:" + str(item) + "Report:" + str(report))
        if report.when == "setup" and report.outcome == 'failed':
            PytestPlugin.send_case_result(item, report.outcome)
        elif report.when == "call":
            PytestPlugin.send_case_result(item, report.outcome)
        else:
            print_info("Item:" + str(item) + "Report:" + str(report))

    @classmethod
    def send_case_result(self, item: Item, result):
            _caseTitle, _caseNo = PytestPlugin.getCaseName(item)
            PytestPlugin.jira_convert_allure(_caseTitle, _caseNo)
            if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() == '脚本同步':
                print_info(f'用例编号:{_caseNo}  用例名称:{_caseTitle} 脚本同步完成')
            else:
                PytestPlugin.sent_single_case_result(_caseNo,_caseTitle, result)

    @classmethod
    def sent_single_case_result(self, _caseNo,_caseTitle, result):
        _caseTitleList = []
        _caseList = []
        if DataProcess.isNotNull(_caseTitle):
            _caseTitleList = _caseTitle.split(';')
        if DataProcess.isNotNull(_caseNo) and _caseNo != '00000':
            _caseTitleList.extend(_caseNo.split(';'))
        if DataProcess.isNotNull(_caseTitleList) > 0:
            _caseTitleList = DataProcess.list_dict_duplicate_removal(_caseTitleList)
            for temp in _caseTitleList:
                info = ATFPlatForm.getCaseInfoByNameOrID(temp)
                _caseList.append(info['key'])
        if DataProcess.isNotNull(_caseList) > 0:
            caseInfoList = ""
            _caseList = DataProcess.list_dict_duplicate_removal(_caseList)
            for temp in _caseList:
                if DataProcess.isNotNull(temp) and temp.strip() != '00000':
                    info = ATFPlatForm.getCaseInfoByNameOrID(temp)
                    if result != 'skipped' and info['key'] != '00000':
                        caseInfoList = caseInfoList + info['summary'] + "(" + info['key'] + "),"
                        ATFPlatForm.sent_result_byCaseName(info['summary'], info['key'], result, "")
                    else:
                        caseInfoList = caseInfoList + temp + "(" + info['key'] + "),"
            if result != Constant.STATUS_AUTOTEST:
                print_debug(f"---用例列表:{caseInfoList}  执行状态:{result}")
        else:
            logger.info(f"---用例列表:无用例列表【请检查是否设置用例名称或者编号】 执行状态:{result}")

    @classmethod
    def sync_case_Script(self, item: Item, _caseTitle, _caseNo):
        _caseurl = PytestPlugin.getCaseUrl(item)
        _caseTitleList = []
        if DataProcess.isNotNull(_caseTitle):
            _caseTitleList = _caseTitle.split(';')
        if DataProcess.isNotNull(_caseNo) and _caseNo != '00000':
            _caseTitleList.extend(_caseNo.split(';'))
        if DataProcess.isNotNull(_caseTitleList):
            caseInfoList = ""
            if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() == '脚本同步':
                for _name in _caseTitleList:
                    if DataProcess.isNotNull(_name) and _name != '00000':
                        info = ATFPlatForm.getCaseInfoByNameOrID(_name)
                        caseInfoList = caseInfoList + _name + "(" + info['key'] + "),"
                        MysqlPlatForm.sync_autotest_script(info['summary'], info['key'], info['priority'], _caseurl)
                logger.info(f"---用例列表：{caseInfoList} 脚本路径:{_caseurl}  执行状态:用例同步完成")
                assert "测试用例检查" == "脚本用例同步【执行中断】"
            if PytestPlugin.checkCaseRun(item, _caseTitle, _caseNo):
                logger.info(f"---获取用例列表:{_caseTitleList} 脚本路径:{_caseurl} 执行状态:开始执行")
            else:
                logger.info(f"---获取用例列表:{_caseTitleList} 脚本路径:{_caseurl} 执行状态:执行中断")
                assert "测试用例检查" == "未在测试周期中【执行中断】"
        else:
            logger.info(f"---用例列表:无用例列表【请检查是否设置用例名称或者编号】")
            assert "测试用例检查" == "无用例列表【执行中断】"


    @classmethod
    def checkCaseRun(self,item: Item, _caseTitle, _caseNo):
        isRun = False
        if DataProcess.isNotNull(get_system_key(Constant.TEST_SRTCYCLE_ID)):
            _caseurl = PytestPlugin.getCaseUrl(item)
            _caseTitleList = []
            if DataProcess.isNotNull(_caseTitle):
                _caseTitleList = _caseTitle.split(';')
            if DataProcess.isNotNull(_caseNo):
                _caseTitleList.extend(_caseNo.split(';'))
            print_debug("需要执行用例列表Meta:"+str(_caseTitleList))
            if DataProcess.isNotNull(_caseTitleList):
                for _name in _caseTitleList:
                    if DataProcess.isNotNull(_name) and _name.strip() != '00000':
                        run = ATFPlatForm.getCaseRun(_name)
                        if run['caserunid'] != '00000':
                            label = ATFPlatForm.getCaseInfoByNameOrID(run['caseid'])['lable']
                            if label.find('生产数据') > -1 and DataProcess.isNotNull(DataBus.get_key('productCount')):
                                logger.info(f"用例信息：{str(run)} 执行状态:生产用例执行中断")
                                isRun = False
                            else:
                                if run['status'] == Constant.STATUS_AUTOTEST or run['status'] == Constant.STATUS_AUTOTEST_PARA:
                                    logger.info(f"用例名称:{_name} 用例信息：{str(run)} 执行状态:用例执行中")
                                    isRun = True
                                else:
                                    logger.info(f"用例名称:{_name} 用例信息：{str(run)} 执行状态:用例状态不在执行中")
                        else:
                            logger.info(f"用例名称:{_name} 用例信息：{str(run)} 执行状态:用例不在执行周期中")
            else:
                _name = _caseTitleList[0]
                run = ATFPlatForm.getCaseRun(_name)
                if run['caserunid'] != '00000':
                    logger.info(f"用例名称:{_name}  用例信息：{str(run)} 执行状态:用例执行中")
                    isRun = True
                else:
                    logger.info(f"用例名称:{_name} 用例信息：{str(run)} 执行状态:用例不在执行周期中")
        else:
            isRun = True
        return isRun

    @classmethod
    def getCaseUrl(self, item:Item):
        filePath = item.fspath.strpath
        projectPath = get_system_key(Constant.CURRENT_PATH)
        filePathName = str(filePath).replace(projectPath, '').strip()[1:]
        fileClassMethod = str(item.__dict__['location'][2]).split('.')
        fileClass = ''
        if fileClassMethod.__len__() > 1:
            fileClass = f'::{fileClassMethod[0]}'
            fileMethond = f'::{fileClassMethod[1]}'

        else:
            fileMethond = f'::{fileClassMethod[0]}'
        caseurl = f'{filePathName}{fileClass}{fileMethond}'
        return caseurl


    @classmethod
    def jira_convert_allure(self, _caseName, _caseNo):
        _caseTitleList = []
        _title = "未设置用例属性信息【请检查装饰器】"
        _info = "未设置用例属性信息【请检查装饰器】"
        if DataProcess.isNotNull(_caseNo) and _caseNo.strip() != '00000':
            _title = _caseNo+"【用例编号未关联测试用例】"
            _info = _caseNo + "【用例编号未关联测试用例】"
            _caseTitleList = _caseTitleList + _caseNo.split(';')
        if DataProcess.isNotNull(_caseName):
            _title = _caseName+"【用例名称未关联测试用例】"
            _info = _caseName + "【用例名称未关联测试用例】"
            _caseTitleList = _caseName.split(';')
        if DataProcess.isNotNull(_caseTitleList):
            _title = ""
            _info = ""
            print_debug(f"Allure用例名称:{_caseTitleList}")
            for temp in _caseTitleList:
                info = ServicePlatForm.getCaseInfo(temp)
                if _title.find(info['summary']+";") < 0:
                    _title = _title+info['summary']+";"
                    if info['key'] != '00000':
                        _info = _info + info['summary']+"【"+info['key']+"】"+";"
                        allure_severity(info['priority'])
                        allure_testcase_link(f"{Constant.JIRA_URL}/browse/{info['key']}", info['summary']+"【"+info['key']+"】")
                    else:
                        _info = _info + info['summary'] + "【00000】"+";"
                        case_link = f'{Constant.JIRA_URL}/browse/'
                        allure_testcase_link(case_link, info['summary']+"【无关联】")
                        allure_severity("P1")
        logger.info("用例信息:"+_info)
        allure_title(_title)









