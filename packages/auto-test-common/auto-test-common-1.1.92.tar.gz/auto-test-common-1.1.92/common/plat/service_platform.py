import json
import time

from common.common.constant import Constant
from common.data.handle_common import get_system_key,print_debug
from common.common.api_driver import APIDriver
from loguru import logger


class ServicePlatForm(object):

    @classmethod
    def sendMsg(self, data):
        try:
            _data = data.encode()
            APIDriver.http_request(url=get_system_key(Constant.MSG_URL), method='post', parametric_key='data',
                                       data=_data)
        except Exception as e:
            logger.info(f'推送Muc:{data} 异常信息' + repr(e))


    @classmethod
    def getCaseByCycle(self, caseName, status, caseId: str = '00000'):
        cycleId = get_system_key(Constant.TEST_SRTCYCLE_ID)
        try:
            response = APIDriver.http_request(url=Constant.ATF_PYTHON_URL+'/jira/cycle/getCase',
                                   method = 'post',
                                   parametric_key = 'json',
                                   data = {"cycleId":cycleId,"caseName":caseName,"caseId":caseId,"status":status},
                                    )
            content = json.loads(response.content)
            return content
        except Exception as e:
            logger.error(f'获取周期编号：{cycleId} 用例名称:{caseName} 用例编号:{caseId} 状态:{status} 异常信息:' + repr(e))


    @classmethod
    def getATFDataSingle(self, projectAlice, env):
        try:
            response = APIDriver.http_request(url=Constant.ATF_API + f'/getParam/{projectAlice}/{env}',
                                              method='get',
                                              )
            content = json.loads(response.content)['data']
            return content
        except Exception as e:
            return repr(e)


    @classmethod
    def getATFData(self, projectAlice, env):
        _result = ""
        for i in range(1, Constant.RETRY_TIME):
            _result = ServicePlatForm.getATFDataSingle(projectAlice, env)
            if type(_result) == dict:
                break
            else:
                _result = ServicePlatForm.getATFDataSingle(projectAlice, env)
                time.sleep(1)
            if i == Constant.RETRY_TIME:
                logger.error(f"获取项目基础数据异常系统编号:{projectAlice} 环境:{env} 异常信息：{_result}")
                _result = None
        return _result

    @classmethod
    def getTestPlanInfo(self,cycleId):
        return json.loads(APIDriver.http_request(url=f"{Constant.ATF_PYTHON_URL}/jira/plan/get/{cycleId}", method='get').content)


    @classmethod
    def updateByRunid(self, runid, result, comment:str = "", steps:str = ""):
        _dict = {'result': result, 'comment': comment, 'steps': steps}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/run/update/{runid}",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict,ensure_ascii=False))
        )

    @classmethod
    def updateCaseRun(self, cycleId, status, rate, result):
        print_debug(f"同步测试结果：周期编号：{cycleId} 状态：{status} 通过率:{rate} 结果:{result}")
        _dict = {'status': status, 'rate': rate, 'result': result}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/send/result/{cycleId}",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict,ensure_ascii=False))
        )


    @classmethod
    def syncCycleCase(self, cycleId):
        if self.isNotNull(get_system_key('Result')):
            _dict = {'status': get_system_key('Result'), 'projectKey':get_system_key(Constant.PORJECT_ID)}
        else:
            _dict = {'status': '', 'projectKey':get_system_key(Constant.PORJECT_ID)}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/sync/{cycleId}",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict, ensure_ascii=False))
        )

    @classmethod
    def syncJiraCaseAndBug(self):
        if self.isNotNull(get_system_key(Constant.PORJECT_ID)):
            _dict = {'projectKey': get_system_key(Constant.PORJECT_ID)}
        else:
            _dict = {'projectKey': ''}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/data/sync",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict, ensure_ascii=False))
        )

    @classmethod
    def updateStausByCycleId(self, cycleId, status):
        _dict = {'status': status}
        APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/update/cycle/status/{cycleId}",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict, ensure_ascii=False))
        )


    @classmethod
    def getCaseRunByNameOrID(self, cycleId, name):
        _dict = {'cycleId': cycleId, 'name': name}
        content = APIDriver.http_request(
            url=f"{Constant.ATF_PYTHON_URL}/jira/run/get",
            method='post',
            parametric_key='json',
            data=json.loads(json.dumps(_dict, ensure_ascii=False))
        )
        return json.loads(content.content)

    @classmethod
    def getCaseInfo(self, caseName):
        _result = ""
        for i in range(1, Constant.RETRY_TIME):
            _result = ServicePlatForm.getSingeCase(caseName)
            if type(_result) == dict:
                break
            else:
                _result = ServicePlatForm.getSingeCase(caseName)
                time.sleep(1)
            if i == Constant.RETRY_TIME:
                logger.error(f"获取用例名称异常:{caseName} 异常信息：{_result}")
                _result = None
        return _result

    @classmethod
    def getCaseInfoByNameOrID(self, issueKey, caseName:str=""):
        info = {'key':'00000'}
        if self.isNotNull(issueKey):
            info = ServicePlatForm.getCaseInfo(issueKey)
        if info['key'] == '00000':
                if caseName != "" or caseName != "00000" :
                    info = ServicePlatForm.getCaseInfo(caseName)
        return info


    @classmethod
    def getSingeCase(self,caseName):
        _dict = {'name': caseName}
        _result = ""
        try:
            if self.isNotNull(get_system_key(Constant.PORJECT_ID)):
                projectId = get_system_key(Constant.PORJECT_ID)
                _dict = {'name': caseName, 'projectId': projectId}
                content = APIDriver.http_request(
                    url=f"{Constant.ATF_PYTHON_URL}/jira/case/get",
                    method='post',
                    parametric_key='json',
                    data=json.loads(json.dumps(_dict, ensure_ascii=False))
                )
            else:
                content = APIDriver.http_request(
                    url=f"{Constant.ATF_PYTHON_URL}/jira/case/get",
                    method='post',
                    parametric_key='json',
                    data=json.loads(json.dumps(_dict, ensure_ascii=False))
                )
            _result = content.content
            return json.loads(_result)
        except Exception as e:
            # logger.error(f"获取用例名称:{_dict}  返回内容:{_result} 异常:" + repr(e))
            return repr(e)

    @classmethod
    def getProjectDataSingle(self, projectName, projectKey):
        """
        获取项目数据
        :param projectName: 项目别名
        :param projectKey: 关键词
        :return:
        """

        try:
            content = APIDriver.http_request(url=f"{Constant.ATF_URL}/api/getProjectData/{projectName}/{projectKey}",
            method='get')
            return (json.loads(content.content)["data"]["projectValue"])
        except Exception as e:
            return None

    @classmethod
    def getProjectData(self, projectName, projectKey):
        _result = ""
        for i in range(1, Constant.RETRY_TIME):
            _result = ServicePlatForm.getProjectDataSingle(projectName, projectKey)
            if type(_result) != None:
                break
            else:
                _result = ServicePlatForm.getProjectDataSingle(projectName, projectKey)
                time.sleep(1)
            if i == Constant.RETRY_TIME:
                logger.info(f"{Constant.ATF_URL}/api/getProjectData/{projectName}/{projectKey}" + "获取不到value")
                _result = None
        return _result

    @classmethod
    def setProjectData(self, projectKey, value, type=1):
        """
        设置项目数据
        :param projectName: 项目别名
        :param projectKey: 关键词
        :param value: 值
        :param type: 数据类型[0可以重复使用，1不可以重复使用]
        :return:
        """
        if get_system_key('ProjectAlice') is not None and get_system_key('ProjectAlice').strip() != '':
            projectName = get_system_key('ProjectAlice')
            return APIDriver.http_request(
                url=f"{Constant.ATF_URL}/api/setProjectData/{projectName}/{projectKey}/{value}/{type}",
                method='get'
            )

    @classmethod
    def setRedisKey(self, key, value):
        """
        设置项目数据
        :param projectName: 项目别名
        :param projectKey: 关键词
        :param value: 值
        :param type: 数据类型[0可以重复使用，1不可以重复使用]
        :return:
        """
        if get_system_key('ProjectAlice') is not None and get_system_key('ProjectAlice').strip() != '':
            projectAlice = get_system_key('ProjectAlice')
            _dict ={'projectAlice':projectAlice,'type':'0','scope':'PROJECT','key':key, 'value':value}
            content = APIDriver.http_request(
                url=f"{Constant.ATF_PYTHON_URL}/redis/set/key",
                method='post',
                parametric_key='json',
                data=json.loads(json.dumps(_dict, ensure_ascii=False))
            )

    @classmethod
    def getRedisKey(self, key):
        """
        设置项目数据
        :param projectName: 项目别名
        :param projectKey: 关键词
        :param value: 值
        :param type: 数据类型[0可以重复使用，1不可以重复使用]
        :return:
        """
        try:
            if get_system_key('ProjectAlice') is not None and get_system_key('ProjectAlice').strip() != '':
                projectAlice = get_system_key('ProjectAlice')
                _dict = {'projectAlice': projectAlice, 'type': '0', 'scope': 'PROJECT', 'key': key}
                content = APIDriver.http_request(
                    url=f"{Constant.ATF_PYTHON_URL}/redis/get/key",
                    method='post',
                    parametric_key='json',
                    data=json.loads(json.dumps(_dict, ensure_ascii=False))
                )
                return (json.loads(content.content)[key])
        except Exception as e:
            logger.info(f"{Constant.ATF_URL}/redis/get/key获取不到{key}")
            return Constant.DATA_NO_CONTENT


    @classmethod
    def runDeploy(self, jobName, _pramater):
        """
        推送测试结果
        :param jobName:
        :param _pramater:
        :return:
        """
        _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL}/jenkins/runDeploy/{jobName}",
                                           method='get', parametric_key='params', data=_pramater)
        return _tempdata


    @classmethod
    def db_ops(self, _key, _sql, env: str = Constant.ENV):
        """
        执行SQL操作
        :param _key:
        :param _sql:
        :param env:
        :return:
        """
        _sqltemp = _sql.encode("utf-8").decode("latin1")
        if get_system_key(env) is not None:
            env = get_system_key(env)
        sql_type = _sql.strip().split(" ")[0].lower()
        if "select" == sql_type:
            _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/querySetResult/{_key}/{env}",
                                               method='post', parametric_key='data', data=_sqltemp
                                               )
            logger.info(f"执行sql成功:{_sql}")
            return list(_tempdata.json())
        if "insert" == sql_type or "delete":
            _tempdata = APIDriver.http_request(url=f"{Constant.ATF_URL_API}/doExecute/{_key}/{env}",
                                               method='post', parametric_key='data', data=_sqltemp)
            logger.info(f"执行sql成功:{_sql}")
            return _tempdata.text
        else:
            logger.error("不支持其他语句类型执行，请检查sql")

    @classmethod
    def getCaseRun(self, cycleId, issuekey, name: str = ""):
        run = {'caserunid': '00000', 'caseid': '00000', 'status': '00000', 'casename': '00000'}
        try:
            caseArr = issuekey+";"+name.strip()
            caseArr = caseArr.replace("00000","").replace(";;",";").split(";")
            for temp in caseArr:
                if temp.strip() != "" and temp != "00000":
                    run = self.getCaseRunByNameOrID(cycleId, temp)
                    if run['caserunid'] != '00000':
                        return run
            return run
        except Exception as e:
            logger.error(f"周期编号:{cycleId}  用例编号：{issuekey} 用例名称：{name} 获取周期用例异常:" + repr(e))
            return run

    @classmethod
    def getCaseRunlist(self, cycleId, issuekey, name: str = ""):
        try:
            caseArr = issuekey + ";" + name.strip()
            caseArr = caseArr.replace("00000", "").replace(";;", ";").split(";")
            for temp in caseArr:
                if temp.strip() != "" and temp != "00000":
                    run = self.getCaseRunByNameOrID(cycleId, temp)
                    if run['caserunid'] != '00000':
                        return run
            return run
        except Exception as e:
            logger.error(f"周期编号:{cycleId}  用例编号：{issuekey} 用例名称：{name} 获取周期用例异常:" + repr(e))
            return run

    @classmethod
    def update_redis_case(self, caseName):
        _dict = {'name': caseName}
        _result = ""
        try:
            if self.isNotNull(get_system_key(Constant.PORJECT_ID)):
                projectId = get_system_key(Constant.PORJECT_ID)
                _dict = {'name': caseName, 'projectId': projectId}
                APIDriver.http_request(
                    url=f"{Constant.ATF_PYTHON_URL}/redis/case/update",
                    method='post',
                    parametric_key='json',
                    data=json.loads(json.dumps(_dict, ensure_ascii=False))
                )
            else:
                APIDriver.http_request(
                    url=f"{Constant.ATF_PYTHON_URL}/redis/case/update",
                    method='post',
                    parametric_key='json',
                    data=json.loads(json.dumps(_dict, ensure_ascii=False))
                )
        except Exception as e:
            logger.error(f"获取用例名称:{_dict}  返回内容:{_result} 异常:" + repr(e))

    @classmethod
    def insert_autotest_script(self,gitname, caseid, priority, testname, scriptclass, scriptmethod, scriptname, caseurl, scripturl):
        try:
            _dict = {"gitname": gitname, "caseid": caseid, "priority": priority,
                     "testname": testname, "scriptclass": scriptclass,
                     "scriptmethod": scriptmethod, "scriptname": scriptname, "caseurl": caseurl, "scripturl": scripturl}
            _result = APIDriver.http_request(
                url=f"{Constant.ATF_PYTHON_URL}/db/insert/script",
                method='post',
                parametric_key='json',
                data=json.loads(json.dumps(_dict, ensure_ascii=False))
            )
        except Exception as e:
            logger.error(f"异步保存用例到数据库失败:{_dict}  返回内容:{_result} 异常:" + repr(e))

    @classmethod
    def update_redis_case_byID(self, caseName):
        _dict = {'name': caseName}
        _result = ""
        try:
            APIDriver.http_request(
                url=f"{Constant.ATF_PYTHON_URL}/redis/case/update",
                method='post',
                parametric_key='json',
                data=json.loads(json.dumps(_dict, ensure_ascii=False))
            )
        except Exception as e:
            logger.error(f"获取用例名称:{_dict}  返回内容:{_result} 异常:" + repr(e))

    @classmethod
    def isNotNull(self, data):
        try:
            if isinstance(data, bool):
                return data
            if data is None:
                return False
            if isinstance(data, str):
                _data = data
            else:
                _data = str(data)
            if isinstance(data, list):
                if data.__len__() == 0:
                    return False
                else:
                    for temp in data:
                        if self.isNotNull(temp):
                            return True
                    return False
            if _data is None or _data.strip() == '':
                return False
            else:
                return True
        except Exception as e:
            logger.info('判断数据是否为空异常,数据：' + data)
            return True




if __name__ == '__main__':
    print(ServicePlatForm.getCaseRun("29537","【应急响应系统】【人员信息库-播报用户管理】通知播报分组新增成功 ",""))




