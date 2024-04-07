"""sched 运行"""

import logging
import json
from pathlib import Path
from argparse import ArgumentParser
from vxsched import vxsched, load_modules
from vxutils import loggerConfig, VXContext


def main() -> None:
    parser = ArgumentParser(description="调度器")
    parser.add_argument("-c", "--config", default="etc/config.json", help="配置文件")
    parser.add_argument("-m", "--mod", default="mod", help="事件列表")
    parser.add_argument("-l", "--log", default="", help="日志目录")
    parser.add_argument(
        "-d", "--debug", default=False, help="调试模式", action="store_true"
    )
    args = parser.parse_args()
    level = "DEBUG" if args.debug else "INFO"
    if args.log:
        loggerConfig(level=level, filename=args.log)
        logging.debug("启用日志文件: %s", args.log)
    else:
        loggerConfig(level=level, colored=True)

    configfile = Path(args.config)
    if configfile.exists():
        with open(configfile, "r") as f:
            config = json.load(f)
    else:
        config = {}
    context = VXContext(**config)
    vxsched.set_context(context)
    mod = Path(args.mod)
    if mod.exists():
        load_modules(mod_path=mod)
        vxsched.run()
    else:
        logging.error("模块目录不存在: %s", mod)


if __name__ == "__main__":
    main()
