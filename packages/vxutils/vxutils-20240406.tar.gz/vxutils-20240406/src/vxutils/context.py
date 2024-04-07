"""上下文管理器"""

import json
import configparser
import logging
from pathlib import Path
from typing import Any, OrderedDict, Dict, DefaultDict, Optional, Union
from vxutils.convertors import to_json
from vxutils.decorators import singleton

__all__ = ["VXContext"]


class VXContext(OrderedDict[str, Any]):
    """上下文管理器"""

    def __getattr__(self, name: str) -> Any:
        if name in self:
            return self[name]
        return super().__getattribute__(name)

    def __setattr__(self, name: str, value: Any) -> None:
        self[name] = value

    def __delattr__(self, name: str) -> None:
        del self[name]

    def __str__(self) -> str:
        return f"< {self.__class__.__name__} (id-{id(self)}): {to_json(self)} >"

    def __hash__(self) -> int:
        json_str = to_json(self, sort_keys=True)
        return hash(json_str)


if __name__ == "__main__":
    context = VXContext()
    context.a = 1
    context.b = 2
    context.c = 3
    print(hash(context))
    # context.dump("config.json")
    config = VXConfig()
    print(config)
    # config.env = context
    # config.env = {"a": 1, "b": 2, "c": 3}
    print(config.env)
    # config.env.dburl = "mysql://root:123456@localhost:3306/test"
    # config.hello = "world"
    config.env.dbstr = "mysql://root:74898465@localhost:3306/testdb"
    config.env.dbname = "testdb"
    config.env.os = "linux"
    print(config.db)

    config.save()
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print("delete a")
# *    del context.a
# *    print(context)
# *    try:
# *        print(context.a)
# *    except Exception as e:
# *        print(e)
# *    print(context.b)
# *    print(context.c)
# *    context.a = 1
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    context.a = 4
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    context["a"] = 5
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    context["a"] = 6
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    context["d"] = 7
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print(context.d)
# *    context.d = 8
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print(context.d)
# *    del context.d
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    try:
# *        print(context.d)
# *    except Exception as e:
# *        print(e)
# *    context["d"] = 9
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print(context.d)
# *    del context["d"]
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    try:
# *        print(context.d)
# *    except Exception as e:
# *        print(e)
# *
# *    context["d"] = 10
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print(context.d)
# *    context["d"] = 11
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print(context.d)
# *    context["d"] = 12
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print(context.d)
# *    context["d"] = 13
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
# *    print(context.d)
# *    context["d"] = 14
# *    print(context)
# *    print(context.a)
# *    print(context.b)
# *    print(context.c)
