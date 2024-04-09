from common.data.template_data import *
from common.plat.ATF_platform import ATFPlatForm

class TemplatePlugin(object):

    @classmethod
    def rend_template_str(self, t_str, *args, **kwargs):
        """
           渲染模板字符串, 改写了默认的引用变量语法{{var}}, 换成${var}
                模板中引用变量语法 ${var},
                调用函数 ${fun()}
            :return: 渲染之后的值
        """
        return rend_template_str(t_str, *args, **kwargs)

    @classmethod
    def rend_template_obj(self, t_obj: dict, *args, **kwargs):
        """
           传 dict 对象，通过模板字符串递归查找模板字符串，转行成新的数据
        """
        return rend_template_obj(t_obj, *args, **kwargs)

    @classmethod
    def rend_template_array(self, t_array, *args, **kwargs):
        """
           传 list 对象，通过模板字符串递归查找模板字符串
        """
        return rend_template_array(t_array, *args, **kwargs)

    @classmethod
    def rend_template_any(self, any_obj, *args, **kwargs):
        """渲染模板对象:str, dict, list"""
        return rend_template_any(any_obj, *args, **kwargs)

    @classmethod
    def rend_template(self, any_obj):
        return rend_template(any_obj)

if __name__ == '__main__':
    print(ATFPlatForm.getCaseInfoByNameOrID('验证登录页面统一身份认证登录：账号无权限'))

