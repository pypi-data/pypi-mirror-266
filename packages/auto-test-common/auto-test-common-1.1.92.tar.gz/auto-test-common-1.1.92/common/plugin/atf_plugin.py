from jsonpath import jsonpath
from common.plat.service_platform import ServicePlatForm
from common.config.config import TEST_TARGET_REPORT_PATH,CONFIG_PATH
from common.data.data_process import DataProcess
from common.plugin.data_plugin import DataPlugin
from common.plugin.file_plugin import FilePlugin
from loguru import logger
from common.data.handle_common import get_system_key,print_info,print_debug
from common.plat.jira_platform import JiraPlatForm
from common.plugin.data_bus import DataBus
from common.common.constant import Constant
from common.plat.ATF_platform import ATFPlatForm
from common.autotest.handle_allure import allure_step
import os



class ATFPlugin(object):

    @classmethod
    def db_ops(self,_key, _sql, env: str = Constant.ENV, des: str = "数据库操作"):
        DataBus.save_init_data()
        allure_step(des,f'SQL语句:{_sql}')
        return ServicePlatForm.db_ops(_key, _sql, env)

    @classmethod
    def mongo_db(self,_key,env: str = Constant.ENV):
        """
            返回MongoDB实例
        """
        from common.db.handle_mongo import MongoDB
        return MongoDB.mongo_db(_key,env)

    @classmethod
    def mongo_collection(self, _key, _collection, env: str = Constant.ENV):
        """
            返回MongoDB集合
        """
        from common.db.handle_mongo import MongoDB
        return MongoDB.mongo_collection(_key, _collection, env)

    @classmethod
    def mongo_find(self, _key, _collection, _query, type:str = "", limit:int = 0, _sort:str = "", env: str = Constant.ENV):
        """
            返回查询结果
        """
        from common.db.handle_mongo import MongoDB
        return MongoDB.mongo_find(_key, _collection, _query, type, limit, _sort, env)

    @classmethod
    def sendResult(self, report_html_path: str = TEST_TARGET_REPORT_PATH):
        if DataProcess.isNotNull(get_system_key('type')) and get_system_key('type').strip() != '脚本同步':
            DataBus.save_init_data()
            ATFPlatForm.syncCycleBasic()
            _result, _desc = ATFPlugin.getResultData(report_html_path)
            ATFPlugin.syncJiraCase()
            if _result['result'] == 'success':
                JiraPlatForm.setJiraFlowStatus("2551")
            self.sendMsg(_desc)
            self.getResultScript("'未执行','准备执行'",'未开始执行')
            self.getResultScript("'执行中','参数化执行'", '执行未完成')
            self.getResultScript("'失败'",'执行失败')
            dict = {"issuekey": f'{_result["jirakey"]}', "project": f'{_result["projectName"]}',
                    "result": f'{_result["result"]}'}
            ServicePlatForm.runDeploy("AutoTest-Result", dict)

    @classmethod
    def getResultScript(self, result, desc):
        case_name_list = ATFPlatForm.getCycleByResult(result)
        case_name_list_str = ""
        for temp in case_name_list:
            case_name_list_str = case_name_list_str + temp['script'].replace('test/','') + ","
        logger.info(f"未执行的测试用例【{desc}】:" + case_name_list_str)


    @classmethod
    def sendMsg(self, content):
        if DataProcess.isNotNull(get_system_key(Constant.SEND_URSER_LIST)):
            _list = get_system_key(Constant.SEND_URSER_LIST).split(';')
            for _index in range(len(_list)):
                _arr = str(_list[_index]).split('|')
                os.environ['toUserId'] = str(_arr[0]).lower()
                os.environ['toMail'] = str(_arr[1])
                content = content.replace("&", "&amp;")
                DataBus.set_key('content', content)
                _data = DataBus.get_data(get_system_key('MUC_MSG'))
                logger.info(f'推送MUC消息：{_arr[0]} 邮箱:{_arr[1]}')
                ServicePlatForm.sendMsg(_data)


    @classmethod
    def getResultData(self, report_html_path):
        try:
            _summary = FilePlugin.load_json(f'{report_html_path}/widgets/summary.json')
            _result = dict()
            _result['projectId'] = ""
            _result['projectName'] = ""
            _result['env'] = get_system_key('env')
            _result['jiraLink'] = ''
            _result['jirakey'] = ''
            _result['type'] = ''
            _result['typeInfo'] = ''
            _result['buildUrl'] = get_system_key('BUILD_URL')
            _result['cycleName'] = ''
            _result['cycleNameInfo'] = ''
            _result['passrate'] = 0
            _result['passrateInfo'] = ''
            _result["cycleLink"] = ''
            _result['reportUrl'] = _result['buildUrl'] +"allure/"
            if DataProcess.isNotNull(get_system_key(Constant.PROJECT_NAME)):
                _result['projectName'] = get_system_key(Constant.PROJECT_NAME)
                _result['projectId'] = get_system_key(Constant.PORJECT_ID)
            if DataProcess.isNotNull(get_system_key(Constant.ISSUE_KEY)):
                _result['jiraLink'] = f'计划地址：{get_system_key(Constant.TEST_TestPlan_URL)}\n'
                _result['jirakey'] = get_system_key(Constant.ISSUE_KEY)
            if DataProcess.isNotNull(get_system_key("type")):
                _result['type'] =get_system_key("type")
                _result['typeInfo'] = f'测试类型：{_result["type"]}\n'
            if DataProcess.isNotNull(get_system_key(Constant.TEST_SRTCYCLE_NAME)):
                _result['cycleName'] = get_system_key(Constant.TEST_SRTCYCLE_NAME)
                _result['cycleNameInfo'] = f'周期名称：{get_system_key(Constant.TEST_SRTCYCLE_NAME)}\n'
                _result['cycleLink'] = f'周期地址：{get_system_key(Constant.TEST_SRTCYCLE_URL)}\n'
            if DataProcess.isNotNull(get_system_key('passrate')):
                _result['passrate'] = int(get_system_key('passrate'))
                _result['passrateInfo'] = f'质量阀值：{_result["passrate"]}\n'
            _result['total'] = DataPlugin.get_data_jpath(_summary, "$.statistic.total")
            _result['passed'] = DataPlugin.get_data_jpath(_summary, "$.statistic.passed")
            _result['failed'] = DataPlugin.get_data_jpath(_summary, "$.statistic.failed")
            _result['broken'] = DataPlugin.get_data_jpath(_summary, "$.statistic.broken")
            _result['start'] = DataProcess.getDate(int(str(DataPlugin.get_data_jpath(_summary, "$.time.start")).strip()) / 1000)
            _result['stop'] = DataProcess.getDate(int(str(DataPlugin.get_data_jpath(_summary, "$.time.stop")).strip()) / 1000)
            _result['duration'] = int(str(DataPlugin.get_data_jpath(_summary, "$.time.duration")).strip()) / 1000
            act_passrate = round((int(_result['passed']) / int(_result['total'])) * 100, 2)
            _result['act_passrate'] = act_passrate
            if _result['act_passrate'] > _result['passrate']:
                _result['result'] = 'pass'
                _result['resultInfo'] = f'{act_passrate}' + '%【通过】'
                _result['resultJiraInfo'] = f'{act_passrate}' + '%{color:#00875a}【通过】{color}'
            else:
                _result['result'] = 'fail'
                _result['resultInfo'] = f'{act_passrate}' + '%【失败】'
                _result['resultJiraInfo'] = f'{act_passrate}' + '%{color:#FF0000}【失败】{color}'
            _desc = f'项目名称：{_result["projectName"]}\n' \
                    f'项目编号：{_result["projectId"]}\n' \
                    f'执行环境：{_result["env"]}\n'\
                    f'{_result["typeInfo"]}'\
                    f'{_result["cycleNameInfo"]}'\
                    f'{_result["passrateInfo"]}'\
                    f'总用例数：{_result["total"]}\n' \
                    f'通过用例：{_result["passed"]}\n' \
                    f'失败用例：{_result["failed"]}\n'\
                    f'中断用例：{_result["broken"]}\n' \
                    f'测试结果：{_result["resultInfo"]}\n'\
                    f'运行时间：{_result["duration"]}S\n'\
                    f'开始时间：{_result["start"]}\n'\
                    f'结束时间：{_result["stop"]}\n'\
                    f'构建详情：{_result["buildUrl"]} \n'\
                    f'{_result["jiraLink"]}' \
                    f'{_result["cycleLink"]}' \
                    f'测试报告：{_result["reportUrl"]}\n'
            print_info(f'测试结果数据:\n{_result}')
            logger.info(f'测试结果信息:\n{_desc}')
            ServicePlatForm.updateCaseRun(get_system_key(Constant.TEST_SRTCYCLE_ID), Constant.STATUS_AUTOTEST_DONE, _result['act_passrate'],
                                          _result['result'])
            return _result, _desc
        except Exception as e:
            logger.info(f'获取测试结果异常:' + repr(e))
            ServicePlatForm.updateCaseRun(get_system_key(Constant.TEST_SRTCYCLE_ID), Constant.STATUS_AUTOTEST_DONE,
                                          "0.0%",
                                          "skip")
            return "",""

    @classmethod
    def syncJiraCase(self,report_html_path: str = TEST_TARGET_REPORT_PATH):
        """
        通过测试结果到Jira
        """
        logger.info("开始同步测试用例结果到测试周期")
        buildurl = get_system_key('BUILD_URL')
        temp = FilePlugin.load_json(f'{report_html_path}/data/behaviors.json')
        ATFPlugin.syncStatus(buildurl,temp, 'passed')
        ATFPlugin.syncStatus(buildurl, temp, 'failed')
        ATFPlugin.syncStatus(buildurl, temp, 'broken')
        logger.info("成功同步测试用例结果到测试周期")

    @classmethod
    def syncStatus(self, buildurl, report, status):
        xpath = f"$..children[?(@.status=='{status}')].[name,status,parentUid,uid]"
        testcase = jsonpath(report, xpath)
        if testcase != False and testcase.__len__() > 0:
            caseName = testcase[::4]
            caseStatus = testcase[1::4]
            parentUids = testcase[2::4]
            uids = testcase[3::4]
            print_debug("自动化用例名称:" + str(caseName))
            print_debug("自动化用例结果" + str(caseStatus))
            print_debug("自动化用例uid" + str(uids))
            for i in range(0, len(caseName)):
                parentUid = parentUids[i]
                uid = uids[i]
                _caseurl = f'{buildurl}allure/#behaviors/{parentUid}/{uid}'
                _caseTitleList = caseName[i].split(';')
                for temp in _caseTitleList:
                    ATFPlatForm.sent_result_byCaseName(temp, "", "", _caseurl)




















