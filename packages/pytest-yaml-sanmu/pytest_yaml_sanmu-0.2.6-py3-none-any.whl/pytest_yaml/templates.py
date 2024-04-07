"""
@Filename:   commons/template
@Author:      sanmu
@Time:        2023/2/1 20:23
@Describe:    ...
"""
import copy
import logging
import re
import string

logger = logging.getLogger(__name__)


def _str(s) -> str:
    return f"'{s}'"


class Template(string.Template):
    """
    1. 支持函数调用
    2. 参数也可以是变量
    """

    func_mapping = {
        "str": _str,
        "float": float,
        "bool": bool,
        "int": int,
    }

    call_pattern = re.compile(r"\${(?P<func_name>.*?)\((?P<func_args>.*?)\)}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hot_load()

    def render(self, mapping: dict) -> str:
        s = self.safe_substitute(mapping)  # 原有方法替换变量
        s = self.safe_substitute_funcs(s, mapping)  # 新方法替换函数结果

        return s

    def safe_substitute_funcs(self, template, mapping) -> str:
        """
        解析字符串中的函数名和参数，并将函数调用结果进行替换
        :param template: 字符串
        :param mapping: 上下文，提供要使用的函数和变量
        :return: 替换后的结果
        """

        mapping = copy.deepcopy(mapping)
        mapping.update(self.func_mapping)  # 合并两个mapping

        def convert(mo):
            func_name = mo.group("func_name")
            func_args = mo.group("func_args").split(",")

            func = mapping.get(func_name)  # 读取指定函数
            func_args_value = [mapping.get(arg, arg) for arg in func_args]

            if func_args_value == [""]:
                func_args_value = []

            if not callable(func):
                return mo.group()  # 如果是不可调用的假函数,不进行替换
            else:
                return str(func(*func_args_value))  # 否则用函数结果进行替换

        return self.call_pattern.sub(convert, template)

    def hot_load(self):
        try:
            import yaml_funcs

            logger.info("load funcs by yaml_funcs")
            for func_name in dir(yaml_funcs):  # 遍历模块中的所有函数
                if func_name.startswith("_"):
                    continue

                func_code = getattr(yaml_funcs, func_name)  # 取到了函数对象
                if callable(func_code):  # 如果是一个可以调用的函数
                    self.func_mapping[func_name] = func_code  # 函数放到Template中
        except ImportError:
            ...
