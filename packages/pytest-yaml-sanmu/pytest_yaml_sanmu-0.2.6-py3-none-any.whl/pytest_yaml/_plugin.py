from abc import ABCMeta, abstractmethod

import allure
import pytest
from pytest import FixtureRequest

from .file import YamlItem


class YamlPlugin(metaclass=ABCMeta):
    def __init__(self, config: pytest.Config):
        self.config = config

        self.__name__ = self.__class__.__name__  # 每个插件类，只能注册一次

    @abstractmethod
    def pytest_yaml_run_step(self, item: YamlItem, request: FixtureRequest):
        ...


class PrintYamlPlugin(YamlPlugin):
    @pytest.hookimpl(trylast=True)
    def pytest_yaml_run_step(self, item: YamlItem, request: FixtureRequest):
        print("-" * 10)
        print(f"当前用例id：{item.nodeid}")
        print(f"当前用例名称：{item.name}")
        print(f"当前用例步骤：{item.current_step}")
        print(f"当前用例步骤序号：{item.current_step_no}")
        print(f"最大用例步骤序号：{item.max_step_no}")
        print(f"当前是否第一个步骤：{item.is_first_step}")
        print(f"当前是否最后一个步骤：{item.is_last_step}")

        if item.is_last_step:
            print("=" * 20)


class AllureYamlPlugin(YamlPlugin):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta_column_name = ""

    @pytest.hookimpl(tryfirst=True)
    def pytest_yaml_run_step(self, item: YamlItem, request: FixtureRequest):
        key = list(item.current_step)[0]
        value = list(item.current_step.values())[0]

        if not key.startswith("allure"):
            return None
        if not value:
            return None

        label = key.split("_")[-1]

        if label == "step":
            with allure.step(value):
                ...
        else:
            f = getattr(allure.dynamic, label)
            f(value)

        return True
