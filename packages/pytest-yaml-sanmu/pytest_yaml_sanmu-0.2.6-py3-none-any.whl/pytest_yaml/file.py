import itertools
import logging
from pathlib import Path
from typing import Any, Iterable, Union

import pytest
import yaml
from yamlinclude import YamlIncludeConstructor

from .models import Case
from .templates import Template

logger = logging.getLogger(__name__)


class MySafeLoader(yaml.SafeLoader):
    pass


class MyYamlInclude(YamlIncludeConstructor):
    def _read_file(self, path, loader, encoding):
        path = str(Path(loader.name).parent / path)

        return super()._read_file(path, loader, encoding)


MyYamlInclude.add_to_loader_class(loader_class=MySafeLoader)


class YamlFile(pytest.File):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class FakeObj(object):
            __doc__ = self.path

        self.obj = FakeObj

    def collect(self):
        # 加载文件内容

        for case_dict in yaml.load_all(self.path.open(encoding="utf-8"), MySafeLoader):
            case = Case.from_case_dict(case_dict)
            yield from _case_to_yaml_item(case, self)


class YamlItem(pytest.Function):
    yaml_data: Case  # yaml数据内容
    max_step_no: int  # 最大步骤数
    current_step_no: int  # 当前步骤书
    current_step: dict  # 当前步骤内容
    usefixtures: dict  # fixtures

    def __init__(self, *args, own_markers=None, **kwargs):
        if own_markers and hasattr(self, "own_markers"):
            self.own_markers.extend(own_markers)
        super().__init__(*args, **kwargs)
        self.usefixtures = dict()

    @property
    def cls(self):
        return self.__class__

    @property
    def is_first_step(self):
        if self.current_step_no == 0:
            return True

        return False

    @property
    def is_last_step(self):
        if self.current_step_no >= self.max_step_no:
            return True

        return False

    @property
    def location(self):
        location = self.reportinfo()
        relfspath = self.session._node_location_to_relpath(self.path)

        assert type(location[2]) is str
        return relfspath, location[1], location[2]

    @classmethod
    def from_parent(cls, parent, name, case, marks, **kw):
        own_markers = []

        obj: YamlItem = super().from_parent(
            parent,
            name=name,
            callobj=cls._call_obj,
            own_markers=own_markers,
            **kw,
        )
        obj.yaml_data = case
        obj.max_step_no = len(case.steps) - 1

        for mark in marks:
            if isinstance(mark, str):
                mark_name = mark
                mark_args = []
            elif isinstance(mark, dict):
                mark_name = list(mark.keys())[0]
                mark_args = list(mark.values())

            if mark_name == "usefixtures":
                fixture_name_list = mark[mark_name]
                for fixture_name in fixture_name_list:
                    obj.usefixtures.setdefault(fixture_name, "no set")
            else:
                mark_func = getattr(pytest.mark, mark_name)
                mark_obj = mark_func(*mark_args)
                own_markers.append(mark_obj)  # ???
                obj.add_marker(mark_obj)
        logger.debug(f"Generate new test: nodeid={obj.nodeid}, marks={marks} ")
        return obj

    @classmethod
    def from_parent_parametrize(
        cls, parent, name, case: Case, marks, parametrize_marks
    ):
        # logger.warning(f"{marks=}")
        # logger.warning(f"{parametrize_marks=}")

        arg_names = []
        for i in parametrize_marks:
            arg_names.extend(str_or_list(i["parametrize"]["keys"]))

        arg_vals = []
        for i in parametrize_marks:
            vals = i["parametrize"]["vals"]
            arg_vals.append(vals)

        template_case: Case = case.model_copy()
        template_case.mark = [m for m in case.mark if not is_parametrize(m)]
        case_str = template_case.to_yaml()
        # logger.warning(f"{case_str=}")

        for vals in itertools.product(*arg_vals):
            vals = list(get_value_by_sequence(*vals))
            case_yaml = Template(case_str).safe_substitute(dict(zip(arg_names, vals)))
            logger.debug(f"nwe case by parametrize :{case_yaml}")
            new_case = Case.from_yaml(case_yaml)
            new_case.test_name += str(list(vals))

            yield YamlItem.from_parent(
                parent,
                case=new_case,
                name=new_case.test_name,
                marks=new_case.mark,
            )

    def _call_obj(self, request: pytest.FixtureRequest):
        logger.debug(f"runrtest: {self.nodeid}")
        for fixture_name in self.usefixtures:
            logger.debug(f"request fixture: {fixture_name}")
            fixture_value = request.getfixturevalue(fixture_name)
            logger.debug(f"fixture value is: {fixture_value}")
            self.usefixtures[fixture_name] = fixture_value

        for i, step in enumerate(self.yaml_data.steps):
            self.current_step_no = i
            self.current_step = step
            request.config.hook.pytest_yaml_run_step(
                item=self,
                request=request,
            )

    def runtest(self) -> None:
        funcargs = self.funcargs
        testargs = {arg: funcargs[arg] for arg in self._fixtureinfo.argnames}

        self._call_obj(**testargs)

    def repr_failure(self, excinfo):
        style = self.config.getoption("tbstyle", "auto")
        if style == "auto":
            style = "value"

        tb_info = excinfo.traceback[-1]
        file_info = f"{tb_info.path}:{tb_info.lineno}: {excinfo.typename}"
        err_info = f"{self._repr_failure_py(excinfo, style=style)}"

        str_l = [
            "",
            file_info,
            err_info,
        ]
        if getattr(self, "current_step_no", -1) >= 0:  # 步骤已经开始执行
            str_l[0] = "Yaml Content: \n" + self.yaml_data.to_yaml()

        # logger.warning(str_l[0])
        return "\n".join(str_l)


def _case_to_yaml_item(
    case: Case, parent: YamlFile
) -> Iterable[Union[pytest.Item, pytest.Collector]]:
    parametrize_marks = []
    other_marks = []

    for mark in case.mark:
        if is_parametrize(mark):
            parametrize_marks.append(mark)
        else:
            other_marks.append(mark)

    if parametrize_marks:
        yield from YamlItem.from_parent_parametrize(
            parent,
            case=case,
            name=case.test_name,
            marks=other_marks,
            parametrize_marks=parametrize_marks,
        )
    else:
        yield YamlItem.from_parent(
            parent,
            case=case,
            name=case.test_name,
            marks=case.mark,
        )


def is_parametrize(mark):
    if isinstance(mark, dict) and "parametrize" in mark:
        return True
    else:
        return False


def str_or_list(x: Union[str, list]) -> list:
    if isinstance(x, list):
        return x
    else:
        return [x]


def list_or_nestlist(x: Union[list[Any], list[list]]) -> list[list]:
    try:
        _ = x[0][0]
        return x
    except TypeError:
        return [x]


def get_value_by_sequence(*args):
    """

    [["username, id"], "password"] ->  ["username, id", "password"]
    [[1,9],[2,99],[3,999]]    -> [1,9,2,99,3,999]

    :param args:
    :return:
    """
    for arg in args:
        if type(arg) in [list, tuple]:
            yield from arg
        else:
            yield arg
