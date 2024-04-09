import datetime
import os

from loguru import logger
from common.data.handle_common import get_system_key,format_caseName
from common.common.constant import Constant
from common.db.handle_db import MysqlDB
from common.plat.jira_platform import JiraPlatForm
from common.data.data_process import DataProcess
from common.plat.service_platform import ServicePlatForm


class MysqlPlatForm(object):

    @classmethod
    def get_case_byCycle(self,caseName):
        _config = {'key': 'atf'}
        _mysql = MysqlDB(_config)
        caseName = format_caseName(caseName)
        cycleId = get_system_key(Constant.TEST_SRTCYCLE_ID)
        _sql = f"select * from test_autotest_run where  casename ='{caseName}' and cycleId ='{cycleId}' "
        _list = _mysql.execute(_sql).fetchall()
        _mysql.conn.commit()
        _mysql.close()
        return _list[0]

    @classmethod
    def sync_autotest_script(self, testname, caseid, priority, caseurl):
        if DataProcess.isNotNull(get_system_key(Constant.GIT_PROJECTNAME)) and DataProcess.isNotNull(testname):
            testname, gitname, scripturl, scriptclass, scriptmethod, scriptname = DataProcess.getCaseUrlMeta(testname,
                                                                                                             caseurl)
            if DataProcess.isNotNull(scripturl):
                if caseid != '00000':
                    MysqlPlatForm.updateDesAndRefer(caseid,testname,scripturl,caseurl)
                else:
                    logger.info(f'Jira用例和脚本关系成功失败【未找到用例编号】：用例编号：{caseid} 用例名称:{testname} 脚本路径:{caseurl}')
                ServicePlatForm.insert_autotest_script(gitname, caseid, priority, testname, scriptclass, scriptmethod, scriptname, caseurl, scripturl)

    @classmethod
    def updateDesAndRefer(self,caseid,testname,scripturl,caseurl):
        _dict = ServicePlatForm.getCaseInfo(caseid)
        script = _dict['script']
        if script.strip() == caseurl.strip():
            logger.info(f'无需保存Jira用例和脚本关系成功【脚本未改变】：用例编号：{caseid} 用例名称:{testname} 当前脚本路径:{caseurl} 原脚本路径:{script}')
        else:
            JiraPlatForm.updateDescription(caseid, scripturl)
            JiraPlatForm.updateTestReference(caseid, caseurl)
            ServicePlatForm.update_redis_case(testname)
            ServicePlatForm.update_redis_case(caseid)
            ServicePlatForm.update_redis_case_byID(caseid)
            logger.info(f'保存Jira用例和脚本关系成功【脚本有改变】：用例编号：{caseid} 用例名称:{testname} 当前脚本路径:{caseurl} 原脚本路径:{script}')


    @classmethod
    def delete_autotest_script(self, caseid):
        if DataProcess.isNotNull(get_system_key(Constant.GIT_PROJECTNAME)) and DataProcess.isNotNull(caseid):
            gitname = get_system_key(Constant.GIT_PROJECTNAME)
            if caseid != '00000':
                JiraPlatForm.updateDescription(caseid, "", "手工")
                JiraPlatForm.updateTestReference(caseid, "")
                logger.info(f'未发现脚本修改jira中用例类型为手工测试：用例编号:{caseid} ')
            _config = {'key': 'atf'}
            _mysql = MysqlDB(_config)
            _sqlscript = f"delete from `traffic_test`.`test_autotest_script` where testid='{caseid}' and gitname='{gitname}' "
            _script = _mysql.execute(_sqlscript).fetchall()
            _mysql.conn.commit()
            _mysql.close()
            logger.info(f'删除数据库脚本和用例关系：用例编号:{caseid} 类型：脚本为空')

    @classmethod
    def insert_api_data(self, _url, _methond, _header, _data, _reponse_time,_reponse_code):
        _hash = hash(f'{_url}:{_methond}:{_header}:{_data}:{_reponse_time}')
        _data= str(_data).replace("'","")
        _config = {'key':'atf'}
        _date = datetime.datetime.now()
        _project_alice = os.environ['projectalice']
        _sql=f"INSERT INTO `traffic_test`.`base_api_data`(`hash_id`,`project_alice`, `url`,`method`, `data`, `reponse_time`,`reponse_code`, `create_time`) VALUES ('{_hash}','{_project_alice}', '{_url}', '{_methond}', '{_data}', '{_reponse_time}', '{_reponse_code}','{_date}')"
        _mysql = MysqlDB(_config)
        _mysql.execute(_sql)
        _mysql.conn.commit()
        _mysql.close()

    @classmethod
    def getScriptyPathByCaseNameList(self, CaseNameList):
        _config = {'key':'atf'}
        _mysql = MysqlDB(_config)
        sql = f"select distinct(caseurl) from test_autotest_script where `status` = '0'"
        sql += " and testname in (%s)" % ','.join(["'%s'" % testname for testname in CaseNameList])
        _list = _mysql.execute(sql).fetchall()
        _mysql.close()
        return _list


    @classmethod
    def get_test_autotest_run(self, jirakey, cycleId, result:str="'通过','未执行','失败','自动化执行'"):
        _info = []
        _sql = f"select * from `traffic_test`.`test_autotest_run` where jirakey='{jirakey}' and cycleId='{cycleId}' and status in ({result})"
        try:
            _config = {'key':'atf'}
            _mysql = MysqlDB(_config)
            _info = _mysql.execute(_sql).fetchall()
            return _info
        except Exception as e:
            logger.error(f'查询SQL异常：{_sql}')
            return _info

    @classmethod
    def delete_autotest_script_byGitName(self, gitName):
        _info = []
        _sql = f"delete from test_autotest_script where gitname='{gitName}'"
        try:
            _config = {'key': 'atf'}
            _mysql = MysqlDB(_config)
            _info = _mysql.execute(_sql).fetchall()
            _mysql.conn.commit()
            _mysql.close()
            return _info
        except Exception as e:
            logger.error(f'查询SQL异常：{_sql}')
            return _info

    @classmethod
    def get_test_case_info(self, jirakey, cycleId, caseName):
        _config = {'key':'atf'}
        _sql = f"select * from `traffic_test`.`test_autotest_run` where jirakey='{jirakey}' and cycleId='{cycleId}' and casename='{caseName}'"
        _mysql = MysqlDB(_config)
        _info = _mysql.execute(_sql).fetchall()
        return _info

    @classmethod
    def get_test_case_info_ByID(self, jirakey, cycleId, caseid):
        _config = {'key':'atf'}
        _sql = f"select * from `traffic_test`.`test_autotest_run` where jirakey='{jirakey}' and cycleId='{cycleId}' and caseid='{caseid}'"
        _mysql = MysqlDB(_config)
        _info = _mysql.execute(_sql).fetchall()
        return _info


    @classmethod
    def get_api_data(self, _url, _methond, _header, _data, _reponse_time, _reponse_code):
        _config = {'key':'atf'}
        _sql = f"select * from `traffic_test`.`base_api_data` where `url`='{_url}' and `method`='{_methond}' and `data`='{_data}' and `reponse_code`={_reponse_code} "
        _mysql = MysqlDB(_config)
        _time=''
        _info=''
        for _temp in  _mysql.execute(_sql).fetchall():
            _time = str(_temp['reponse_time'])+"S, "+_time
            _info = str(_temp['create_time']) +"执行时间:"+str(_temp['reponse_time']) + "S, " + _info
        return _time, _info










