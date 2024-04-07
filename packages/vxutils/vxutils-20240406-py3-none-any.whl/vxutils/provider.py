"""api工具箱"""

import sys
import logging
import importlib
import json
from pathlib import Path
from abc import ABC
from typing import Union, Dict, Any, Optional
from pydantic import TypeAdapter, ValidationError

try:
    from typing_extensions import TypedDict, NotRequired
except ImportError:
    from typing import TypedDict, NotRequired

# from typing_extensions import TypedDict
from vxutils import VXContext


class ProviderConfig(TypedDict):
    """供应商配置"""

    mod_path: str
    params: NotRequired[Dict[str, Any]]


ProviderConfigAdapter = TypeAdapter(ProviderConfig)


def import_tools(mod_path: Union[str, Path, Any], **params: Any) -> Any:
    """导入工具"""

    if params is None:
        params = {}

    cls_or_obj = mod_path
    if isinstance(mod_path, str):
        if mod_path.find(".") > -1:
            mod_name = mod_path.split(".")[-1]
            class_path = ".".join(mod_path.split(".")[:-1])
            mod = importlib.import_module(class_path)
            cls_or_obj = getattr(mod, mod_name)
        else:
            cls_or_obj = importlib.import_module(mod_path)

    return cls_or_obj(**params) if isinstance(cls_or_obj, type) else cls_or_obj


def import_by_config(config: ProviderConfig) -> Any:
    """根据配置文件初始化对象

    配置文件格式:
    config = {
        'mod_path': 'vxsched.vxEvent',
        'params': {
            "type": "helloworld",
            "data": {
                'mod_path': 'vxutils.vxtime',
            },
            "trigger": {
                "mod_path": "vxsched.triggers.vxIntervalTrigger",
                "params":{
                    "interval": 10
                }
            }
        }
    }

    """
    if not isinstance(config, dict):
        return config

    if "mod_path" not in config:
        return config

    mod_path = config["mod_path"]
    params = {}
    if "params" in config and isinstance(config["params"], dict):
        for k, v in config["params"].items():
            try:
                v = ProviderConfigAdapter.validate_python(v)
                params[k] = import_by_config(v)
            except ValidationError:
                params[k] = v

    return import_tools(mod_path, **params)


class AbstractProvider(ABC):
    """接口基类"""

    @property
    def context(self) -> VXContext:
        """上下文管理器"""
        return self._context

    def start_up(self, context: VXContext) -> None:
        """启动接口

        Arguments:
            context {VXContext} -- 上下文
        """
        self._context = context

    def tear_down(self, error: Optional[Exception] = None) -> None:
        """关闭接口"""

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class AbstractProviderCollection(ABC):
    """接口集合基类

    {
        "current": {
            "mod_path": "xxx.xxx",
            "params": {
                "token": "xxxx"
            }
        }",
        "daily_bar": {
            "mod_path": "xxx.xxx",
            "params": {
                "token": "@current"
            }
        }"
        }
    }

    """

    __defaults__: Dict[str, ProviderConfig] = {}

    def __init__(
        self,
        providers: Optional[Dict[str, ProviderConfig]] = None,
        *,
        context: Optional[VXContext] = None,
    ) -> None:
        self._context = VXContext() if context is None else context
        self._providers: Dict[str, Any] = {}
        provider_configs = {**self.__defaults__}
        if providers:
            provider_configs.update(providers)
        self.register_providers(provider_configs)

    @classmethod
    def from_config(
        cls, config: Union[str, Path], *, context: Optional[VXContext] = None
    ) -> "AbstractProviderCollection":
        """从配置文件初始化

        Arguments:
            config {Union[str, Path]} -- 配置文件路径
            context {Optional[VXContext]} -- 上下文
        """
        with open(config, "r", encoding="utf-8") as f:
            provider_configs = json.load(f)
        return cls(provider_configs, context=context)

    @property
    def context(self) -> Union[VXContext, Dict[str, Any]]:
        """上下文管理器"""
        return self._context

    def __str__(self) -> str:
        return f"< {self.__class__.__name__} (id-{id(self)}) >"

    def __getattr__(self, name: str) -> Any:
        if name in self._providers:
            return self._providers[name]
        return super().__getattribute__(name)

    def register_providers(self, provider_configs: Dict[str, ProviderConfig]) -> None:
        """注册启动接口集合"""
        for name, provider_config in provider_configs.items():
            try:
                provider = import_by_config(
                    ProviderConfigAdapter.validate_python(provider_config)
                )
            except ValidationError:
                provider = provider_config
            except Exception as err:
                logging.error(
                    "加载provider: %s (%s)出错: %s", name, provider_config, err
                )
                continue

            if hasattr(provider, "start_up"):
                provider.start_up(self.context)
            self._providers[name] = provider
            logging.info("注册 %s 接口成功..", name)

    def unregister_providers(self, error: Optional[Exception] = None) -> None:
        """注销并关闭接口集合"""
        for name, provider in self._providers.items():
            try:
                provider.tear_down(error)
            except Exception as err:
                logging.error("关闭provider: %s 出错: %s", name, err, exc_info=True)
        self._providers.clear()


if __name__ == "__main__":
    # print(isinstance(AbstractProvider(), type))
    # print(import_tools(mod_path="multiprocessing.dummy.Pool", params={}))
    d = import_by_config(
        config={"mod_path": "multiprocessing.dummy.Pool", "params": {}}
    )
    print(d)
    print(d())
    d = ProviderConfigAdapter.validate_python(
        {"mod_path": "multiprocessing.dummy.Pool", "params": {}}
    )
    print(d)
