import inspect
import logging
from pathlib import Path

import pytest

from . import _plugin
from .file import YamlFile

# from pytest_yml.settings import settings

logger = logging.getLogger(__name__)
enable_plugin = False


def pytest_addhooks(pluginmanager):
    from . import hooks

    pluginmanager.add_hookspecs(hooks)


def pytest_addoption(parser):
    parser.addini(
        "run_yaml_case",
        type="bool",
        default=False,
        help="是否执行yaml测试用例",
    )


def pytest_configure(config: pytest.Config):
    global enable_plugin
    enable_plugin = config.getini("run_yaml_case")

    if not enable_plugin:
        return

    for plug, dist in config.pluginmanager.list_plugin_distinfo():
        if plug.__name__ == "pytest_yaml.plugin":
            dist.metadata = dist.metadata.json
            dist.metadata["name"] = "pytest-yaml"

    for klass_name, klass in inspect.getmembers(
        _plugin,
        lambda x: isinstance(x, type)
        and issubclass(x, _plugin.YamlPlugin)
        and x is not _plugin.YamlPlugin,
    ):
        config.pluginmanager.register(klass(config))


def pytest_collect_file(parent, file_path: Path):
    if not enable_plugin:
        return

    if file_path.suffix in [".yaml", ".yml"] and file_path.name.startswith("test"):
        logger.debug(f"YamlFile: {file_path.absolute()}")
        return YamlFile.from_parent(parent, path=file_path)
