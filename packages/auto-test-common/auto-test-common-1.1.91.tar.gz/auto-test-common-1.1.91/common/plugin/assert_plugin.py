from common.autotest.handle_assert import *

class AssertPlugin(object):
    @classmethod
    def assert_result(self, res: dict, expect_str: str='断言检查'):
        """
         预期结果实际结果断言方法
           :param res: 实际响应结果
           :param expect_str: 预期响应内容，从excel中读取
           return None
        """
        assert_result(res, expect_str)

    @classmethod
    def assert_response(self,res,expect_str: str='断言检查'):
        """
        判断返回报告是否符合预期
        res： response
        expect_str：json 字符串
        """
        assert_response(res, expect_str)

    @classmethod
    def assert_equal_object(self, res, expect_str: str = '断言检查'):
        """
               断言对象是否相等
               res：object
               expect_str： object
               desc：断言描述
               """
        assert_equal_object(res, expect_str)

    @classmethod
    def assert_equal(self, res, expect_str, desc:str='断言检查'):
        """
        断言相等比较
        res：string
        expect_str： string
        desc：断言描述
        """
        assert_equal(res, expect_str, desc)

    @classmethod
    def assert_excel_contain(self, res: dict, expect_str: str='断言检查'):
        """
                    预期结果实际结果断言方法
                   :param res: 实际响应结果Response
                   :param expect_str: 预期响应内容，从excel中读取
                   return None
               """
        assert_excel_contain(res, expect_str)

    @classmethod
    def assert_contain_response(self, res, expect_str: str='断言检查'):
        """
            预期结果实际结果断言方法
            :param res: 实际响应结果Response
            :param expect_str: 预期响应内容，从excel中读取
            return None
        """
        assert_contain_response(res, expect_str)

    @classmethod
    def assert_equals(self, res, expect_str,desc:str='断言检查'):
        """
            判断多个值
            :res：List,String,dict
            :expect_str: List,String,dict
        """
        assert_equals(res, expect_str, desc)

    @classmethod
    def assert_contains(self, res, expect_str, desc:str='断言检查'):
        assert_contains(res, expect_str, desc)

    @classmethod
    def assert_Nobank(self, res, desc:str='断言检查'):
        assert_Nobank(res, desc)

    @classmethod
    def assert_bank(self,res, desc:str='断言检查'):
        assert_bank(res, desc)

    @classmethod
    def assert_not_contains(self, res, expect_str, desc:str='断言检查'):
        assert_not_contains(res, expect_str, desc)

    @classmethod
    def assert_scene_result(self, res, expect_dict):
        assert_scene_result(res, expect_dict)

    @classmethod
    def compare_data(self,set_key, src_data, dst_data, noise_data, num):
        return compare_data(set_key, src_data, dst_data, noise_data, num)

    @classmethod
    def equals(self,check_value, expect_value):
        equals(check_value, expect_value)

    @classmethod
    def less_than(self,check_value, expect_value):
        less_than(check_value, expect_value)

    @classmethod
    def less_than_or_equals(self,check_value, expect_value):
        less_than_or_equals(check_value, expect_value)

    @classmethod
    def greater_than(self,check_value, expect_value):
        greater_than(check_value, expect_value)

    @classmethod
    def greater_than_or_equals(self,check_value, expect_value):
        greater_than_or_equals(check_value, expect_value)

    @classmethod
    def not_equals(self,check_value, expect_value):
        not_equals(check_value, expect_value)

    @classmethod
    def string_equals(self,check_value, expect_value):
        string_equals(check_value, expect_value)

    @classmethod
    def length_equals(self,check_value, expect_value):
        length_equals(check_value, expect_value)

    @classmethod
    def length_greater_than(self,check_value, expect_value):
        length_greater_than(check_value, expect_value)

    @classmethod
    def length_greater_than_or_equals(self,check_value, expect_value):
        length_greater_than_or_equals(check_value, expect_value)

    @classmethod
    def length_less_than(self,check_value, expect_value):
        length_less_than(check_value, expect_value)

    @classmethod
    def length_less_than_or_equals(self,check_value, expect_value):
        length_less_than_or_equals(check_value, expect_value)

    @classmethod
    def contains(self,check_value, expect_value):
        contains(check_value, expect_value)

    @classmethod
    def contained_by(self,check_value, expect_value):
        contained_by(check_value, expect_value)

    @classmethod
    def regex_match(self,check_value, expect_value):
        regex_match(check_value, expect_value)

    @classmethod
    def startswith(self,check_value, expect_value):
        startswith(check_value, expect_value)

    @classmethod
    def endswith(self,check_value, expect_value):
        endswith( check_value, expect_value)








