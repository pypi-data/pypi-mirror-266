"""事件类型"""

import uuid
import logging
from time import time
from datetime import datetime
from enum import Enum
from heapq import heappop, heappush

from queue import Queue, Empty, Full
from contextlib import suppress
from functools import reduce
from typing import (
    Dict,
    Any,
    Set,
    Tuple,
    Optional,
    no_type_check,
    List,
    Union,
    Generator,
)
from pydantic import UUID4, Field, PlainValidator
from vxutils import VXDatetime, to_vxdatetime, to_enum
from vxutils.datamodel.core import VXDataModel

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated


_delta = 0.1


class TriggerStatus(Enum):
    """事件状态"""

    PENDING = "Pending"
    RUNNING = "Running"
    COMPLETE = "COMPLETE"
    UNKNOWN = "UNKNOWN"


class VXTrigger(VXDataModel):
    trigger_dt: Annotated[VXDatetime, PlainValidator(to_vxdatetime)] = Field(
        default_factory=VXDatetime.now
    )
    interval: float = 0

    start_dt: Annotated[VXDatetime, PlainValidator(to_vxdatetime)] = Field(
        default_factory=VXDatetime.now
    )
    end_dt: Annotated[VXDatetime, PlainValidator(to_vxdatetime)] = Field(
        default=VXDatetime.max
    )
    skip_holiday: bool = False
    status: Annotated[
        TriggerStatus, PlainValidator(lambda v: to_enum(v, TriggerStatus.PENDING))
    ] = TriggerStatus.PENDING

    __holidays__: Set[VXDatetime] = set()

    @no_type_check
    def model_post_init(self, __context: Any) -> None:
        if self.start_dt > self.end_dt:
            raise ValueError("开始时间不能大于结束时间")

        if self.status != TriggerStatus.PENDING:
            return
        return super().model_post_init(__context)

    def __lt__(self, other: "VXTrigger") -> bool:
        return self.trigger_dt < other.trigger_dt

    def _get_first_trigger_dt(self) -> Tuple[VXDatetime, TriggerStatus]:

        if self.interval == 0:
            return self.start_dt, TriggerStatus.RUNNING

        if self.end_dt < VXDatetime.now() + _delta:
            return VXDatetime.max, TriggerStatus.COMPLETE

        if self.start_dt + _delta >= VXDatetime.now():
            return self.start_dt, TriggerStatus.RUNNING

        trigger_dt = self.start_dt + self.interval * (
            (VXDatetime.now() - self.start_dt) // self.interval + 1
        )
        if trigger_dt > self.end_dt:
            return VXDatetime.max, TriggerStatus.COMPLETE
        else:
            return trigger_dt, TriggerStatus.RUNNING

    def _get_next_trigger_dt(self) -> Tuple[VXDatetime, TriggerStatus]:

        if self.interval == 0:
            return VXDatetime.max, TriggerStatus.COMPLETE

        trigger_dt = self.trigger_dt + self.interval
        while self.skip_holiday and trigger_dt.date() in self.__holidays__:
            delta = VXDatetime.today() + 60 * 60 * 24 - trigger_dt
            trigger_dt += (delta // self.interval + 1) * self.interval

        if self.trigger_dt + self.interval > (self.end_dt - _delta):
            return VXDatetime.max, TriggerStatus.COMPLETE
        else:
            return trigger_dt, TriggerStatus.RUNNING

    @classmethod
    def add_holidays(cls, holidays: Set[Union[VXDatetime, datetime]]) -> None:
        cls.__holidays__.update((to_vxdatetime(h) for h in holidays))

    def __next__(self) -> "VXTrigger":

        if self.status == TriggerStatus.PENDING:
            self.trigger_dt, self.status = self._get_first_trigger_dt()
        elif self.status == TriggerStatus.RUNNING:
            self.trigger_dt, self.status = self._get_next_trigger_dt()

        if self.status == TriggerStatus.COMPLETE:
            raise StopIteration

        return self

    def __iter__(self) -> Generator[Tuple[str, Any], None, None]:
        return self

    @classmethod
    @no_type_check
    def once(cls, trigger_dt: Optional[VXDatetime] = None) -> "VXTrigger":
        if not trigger_dt:
            trigger_dt = VXDatetime.now()
        data = {
            "status": "Pending",
            "trigger_dt": trigger_dt,
            "start_dt": trigger_dt,
            "end_dt": trigger_dt,
            "interval": 0,
            "skip_holiday": False,
        }
        return cls(**data)

    @classmethod
    @no_type_check
    def every(
        cls,
        interval: float,
        *,
        start_dt: Optional[VXDatetime] = None,
        end_dt: Optional[VXDatetime] = None,
        skip_holiday: bool = False,
    ) -> "VXTrigger":
        if not start_dt:
            start_dt = VXDatetime.now()
        if not end_dt:
            end_dt = VXDatetime.max
        data = {
            "status": "Pending",
            "trigger_dt": start_dt,
            "start_dt": start_dt,
            "end_dt": end_dt,
            "interval": interval,
            "skip_holiday": skip_holiday,
        }
        return cls(**data)

    @classmethod
    @no_type_check
    def daily(
        cls,
        timestr: str = "00:00:00",
        freq: int = 1,
        *,
        start_dt: Optional[VXDatetime] = None,
        end_dt: Optional[VXDatetime] = None,
        skip_holiday: bool = False,
    ) -> "VXTrigger":
        """创建每日执行的触发器

        Keyword Arguments:
            timestr {str} -- 时间点 (default: {"00:00:00"})
            freq {int} -- 日期间隔，单位：天 (default: {1})
            start_dt {Optional[VXDatetime]} -- 开始时间 (default: {None})
            end_dt {Optional[VXDatetime]} -- 结束事件 (default: {None})
            skip_holiday {bool} -- 是否跳过工作日 (default: {False})

        Returns:
            VXTrigger -- 触发器
        """
        if not start_dt:
            start_dt = VXDatetime.now()
        if not end_dt:
            end_dt = VXDatetime.max
        data = {
            "status": "Pending",
            "trigger_dt": start_dt,
            "start_dt": start_dt.combine(
                start_dt.date(), VXDatetime.strptime(timestr, "%H:%M:%S").time()
            ),
            "end_dt": end_dt,
            "interval": 86400 * freq,
            "skip_holiday": skip_holiday,
        }

        return cls(**data)


class VXEvent(VXDataModel):
    id: UUID4 = Field(default_factory=uuid.uuid4)
    type: str = ""
    data: Dict[str, Any] = Field(default_factory=dict, frozen=True)
    priority: int = 10
    channel: str = "default"
    reply_to: str = ""


class VXEventQueue(Queue):
    """消息队列"""

    def _init(self, maxsize: int = 0) -> None:
        self.queue: List[Tuple[VXTrigger, VXEvent]] = []

    def _qsize(self) -> int:
        now = VXDatetime.now()
        return len([1 for t, e in self.queue if t.trigger_dt <= now])
        # return reduce(lambda x, y: 1 if y[0].trigger_dt-0.01 <= now else 0, self.queue, 0)

    # @no_type_check
    def put(
        self,
        event: Union[VXEvent, Tuple[VXTrigger, VXEvent]],
        block: bool = True,
        timeout: Optional[float] = None,
        *,
        trigger: Optional[VXTrigger] = None,
    ) -> None:

        if isinstance(event, (list, tuple, set)):
            trigger, event = event
        elif isinstance(event, VXEvent) and (not trigger):
            trigger = VXTrigger.once()
        item = (trigger, event)
        return super().put(item, block, timeout)

    @no_type_check
    def _put(self, item: Tuple[VXTrigger, VXEvent]) -> None:
        with suppress(StopIteration):
            next(item[0])
            heappush(self.queue, item)

    def _get(self) -> VXEvent:
        trigger, event = heappop(self.queue)
        if trigger.status == TriggerStatus.RUNNING:
            self._put((trigger, event))
            self.unfinished_tasks += 1
            self.not_empty.notify()
        return event

    def get(self, block: bool = True, timeout: Optional[float] = None) -> VXEvent:
        """Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        """
        with self.not_empty:
            if not block and (not self._qsize()):
                raise Empty

            if timeout is not None and timeout <= 0:
                raise ValueError("'timeout' must be a non-negative number")

            if timeout is not None:
                endtime = time() + timeout
            else:
                endtime = VXDatetime.max

            while not self._qsize():
                now = time()
                if now >= endtime:
                    raise Empty

                lastest_trigger_dt = (
                    endtime
                    if not self.queue
                    else self.queue[0][0].trigger_dt.timestamp()
                )
                min_endtime = min(endtime, lastest_trigger_dt, now + 1)
                remaining = min_endtime - now
                self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            return item


ONCE = VXTrigger.once
EVERY = VXTrigger.every
DAILY = VXTrigger.daily


# * if __name__ == "__main__":
# *     event1 = VXEvent(
# *         id="b3976ad7-8223-48ac-b6a7-ba6dc4cbefff",
# *         type="event_1",
# *         data={"a": 1, "b": 2, "c": 3},
# *         status="PENDING",
# *     )
# *
# *event2 = VXEvent(
# *    type="event_2",
# *    data={"a": 1, "b": 2, "c": 3},
# *    status="PENDING",
# *)

# print(event2 < event1)
# event1.trigger_dt = event2.trigger_dt + 1
# print(event1)
# * print("=" * 80)
# t2 = VXTrigger.once(time() + 5)
# * t2 = VXTrigger.every(
# *     3,
# *     start_dt=VXDatetime.today(timestr="09:30:00"),
# *     end_dt=VXDatetime.today(timestr="15:00:00"),
# * )
# * t1 = VXTrigger.daily(
# *     "10:10:00", freq=2, start_dt=VXDatetime.now() + 2, end_dt="2024-03-08 23:59:59"
# * )
# * q = VXEventQueue()
# q.put(event1, trigger=t1)
# * q.put(event1, trigger=t2)
# * while len(q.queue) > 0:
# *         logging.error(
# * "队列状态: %s, %s,下一次执行时间: %s",
# * q.qsize(),
# * len(q.queue),
# * q.queue[0][0].trigger_dt,
# * )
# * with suppress(Empty):
# *             event = q.get(timeout=1)
# * logging.info("+=" * 40)
# * logging.warning("获取信息:  %s", event.type)
# * logging.info("+=" * 40)

# t2 = VXTrigger.daily("15:32:00")
# print("t2:", t2)
# for t in t2:
#    print(t.trigger_dt, t.status)
#    break

# print(t1)
# for t in t1:
#    print(t.trigger_dt, t.status)
# print(t1)

# print(trigger)
# for t in trigger:
#    print("触发：", t.trigger_dt)
# try:
#    while True:
#        next(trigger)
#        print("触发：", trigger.trigger_dt)
# except StopIteration:
#    print("结束。")

# *q = VXEventQueue()
# *q.put(event1)
# *q.put(event2, trigger=trigger)
# *logging.root.setLevel(logging.INFO)
# *logging.info("队列大小：%s", q.queue)
# *import time

# *while True:
# *    logging.info("获取：", q.get(timeout=1))
# *    # logging.info(q.qsize())
# *    if not q.qsize():
# *        break
# *    time.sleep(0.1)
# *    logging.info("队列大小：%s", q.queue)
