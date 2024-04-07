"""事件处理核心模块"""

import os
import logging
import time
from importlib import util, machinery
from pathlib import Path
from typing import Dict, Callable, Any, DefaultDict, Optional, Union, List
from contextlib import suppress
from queue import Empty
from contextlib import suppress
from collections import defaultdict
from vxsched.event import VXEvent, VXEventQueue, VXTrigger
from vxutils import VXContext, async_task, VXAsyncResult

ON_INIT_EVENT = "__init__"
ON_REPLY_EVENT = "__reply__"
ON_TASK_COMPLETE_EVENT = "__task_complete__"
ON_EXIT_EVENT = "__exit__"


class VXScheduler:
    """事件调度器"""

    def __init__(self) -> None:
        self._handlers: DefaultDict[str, List[Callable[[VXContext, VXEvent], Any]]] = (
            defaultdict(list)
        )
        self._queue: VXEventQueue = VXEventQueue()
        self._is_active: bool = False
        # self._eventsources: List[VXEventSource] = []
        self._context = VXContext()

    @property
    def context(self) -> VXContext:
        return self._context

    @property
    def queue(self) -> VXEventQueue:
        return self._queue

    def set_context(self, context: VXContext) -> None:
        self._context = context

    def register(
        self,
        event_type: str,
        callback: Optional[Callable[[VXContext, VXEvent], Any]] = None,
    ) -> Callable[..., Any]:
        """注册事件处理器"""
        if not callback:

            def wrapper(
                func: Callable[[VXContext, VXEvent], Any],
            ) -> Callable[[VXContext, VXEvent], Any]:
                self._handlers[event_type].append(func)
                logging.debug(f"Register event handler: {event_type} -> {callback}")
                return func

            return wrapper

        if callback not in self._handlers[event_type]:
            self._handlers[event_type].append(callback)
            logging.debug(f"Register event handler: {event_type} -> {callback}")
        return callback

    def unregister(
        self, event_type: str, callback: Optional[Callable[..., Any]] = None
    ) -> None:
        """注销事件处理器"""
        if not callback:
            self._handlers.pop(event_type, [])
        elif callback in self._handlers[event_type]:
            self._handlers[event_type].remove(callback)
            logging.debug(f"Unregister event handler: {event_type} -> {callback}")

    @async_task(10, "logging")
    def _run_handler(
        self, callback: Callable[[VXContext, VXEvent], Any], event: VXEvent
    ) -> Any:
        """运行事件

        Arguments:
            callback {Callable[[VXContext, VXEvent], Any]} -- 事件回调函数
            event {VXEvent} -- 事件

        Returns:
            Any -- _description_
        """
        try:
            start = time.perf_counter()
            return callback(self.context, event)
        finally:
            cost = time.perf_counter() - start
            if cost > 1:
                logging.warning(f"Event handler {callback} cost {cost*1000:,.2f}ms")

    def trigger_event(
        self, event: Optional[VXEvent] = None, *, is_async: bool = True
    ) -> Any:
        """触发消息（同步触发）

        Arguments:
            event {Union[str, VXEvent]} -- 待触发的事件

        Returns:
            Any -- 事件返回内容
        """
        result: List[VXAsyncResult] = []
        if isinstance(event, VXEvent):
            result = list(
                self._run_handler(handler, event)
                for handler in self._handlers[event.type]
            )
        else:
            with suppress(Empty):
                while self._queue.qsize():
                    event = self._queue.get(block=False)
                    result.extend(
                        self._run_handler(handler, event)
                        for handler in self._handlers[event.type]
                    )
        return result if is_async else [r.result() for r in result]

    def publish(
        self,
        event: Union[str, VXEvent],
        *,
        trigger: Optional[VXTrigger] = None,
        data: Optional[Dict[str, Any]] = None,
        channel: str = "default",
        priority: int = 10,
        reply_to: str = "",
    ) -> None:
        if isinstance(event, str):
            event = VXEvent(
                type=event,
                data=data or {},
                priority=priority,
                channel=channel,
                reply_to=reply_to,
            )
        self._queue.put(event, trigger=trigger)
        logging.debug(f"Put event: {event} with trigger: {trigger} into queue.")

    def run(self) -> None:
        try:
            if self._is_active is False:
                self._is_active = True
                self.trigger_event(event=VXEvent(type=ON_INIT_EVENT))
                logging.info(f"{'='*10} Scheduler 初始化完成... {'='*10}")
            while self._is_active:
                with suppress(Empty):
                    event = self._queue.get(timeout=1)
                    self.trigger_event(event)
        finally:
            if self._is_active:
                self._is_active = False
                self.trigger_event(event=VXEvent(type=ON_EXIT_EVENT))
                logging.info(f"{'='*10} Scheduler 已停止... {'='*10}")

    def start(self) -> None:
        if self._is_active is False:
            self._is_active = True
            self.trigger_event(event=VXEvent(type=ON_INIT_EVENT))

    def stop(self) -> None:
        if self._is_active is True:
            self._is_active = False
            self.trigger_event(event=VXEvent(type=ON_EXIT_EVENT))

    def run_events(self, events: List[VXEvent]) -> None:
        try:
            self.start()
            for event in events:
                self.trigger_event(event, is_async=False)
        finally:
            self.stop()


sched = VXScheduler()


def load_modules(mod_path: Union[str, Path]) -> Any:
    """加载策略目录"""
    if not os.path.exists(mod_path):
        logging.warning(msg=f"{mod_path} is not exists")
        return

    modules = os.listdir(mod_path)
    logging.info(f"loading strategy dir: {mod_path}.")
    logging.info("=" * 80)
    for mod in modules:
        if (not mod.startswith("__")) and mod.endswith(".py"):
            try:
                loader = machinery.SourceFileLoader(mod, os.path.join(mod_path, mod))
                spec = util.spec_from_loader(loader.name, loader)
                if spec is None:
                    logging.error(f"Load Module: {mod} Failed.")
                    continue

                strategy_mod = util.module_from_spec(spec)
                loader.exec_module(strategy_mod)
                logging.info(f"Load Module: {strategy_mod} Sucess.")
                logging.info("+" * 80)
            except Exception as err:
                logging.error(f"Load Module: {mod} Failed. {err}", exc_info=True)
                logging.error("-" * 80)


if __name__ == "__main__":
    import time
    from vxutils import loggerConfig

    loggerConfig(filename="")

    sched = VXScheduler()

    @sched.register("test")
    @sched.register(ON_INIT_EVENT)
    def test(context: VXContext, event: VXEvent) -> None:
        logging.warning(f"test1: {event.type}")
        time.sleep(2)

    @sched.register("test")
    def test2(context: VXContext, event: VXEvent) -> None:
        logging.warning(f"test2: {event.type}")

    event = VXEvent(type="test")
    sched.publish(event, trigger=VXTrigger.every(1))
    sched.run()
    # time.sleep(2)
