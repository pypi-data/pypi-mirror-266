"""日期工具"""

import time
import calendar
import polars as pl
from datetime import datetime, date, timedelta, tzinfo
from functools import lru_cache
from typing import Union, Optional, Generator, Any, Sequence
from dateutil.parser import parse as dt_parse
from vxutils import Datetime, to_datetime


_min_timestamps = datetime(1980, 1, 1).timestamp()


class VXDatetime(datetime):
    """扩展 datetime 类"""

    __default_timefunc__ = time.time

    @classmethod
    def today(
        cls, tz: Optional[tzinfo] = None, *, timestr: str = "00:00:00"
    ) -> "VXDatetime":

        return cls.combine(date.today(), dt_parse(timestr).time(), tz)

    def __add__(self, __value: Union[timedelta, float, int]) -> "VXDatetime":
        if isinstance(__value, (float, int)):
            __value = timedelta(seconds=__value)
        return super().__add__(__value)

    def __radd__(self, __value: Union[timedelta, float, int]) -> "VXDatetime":
        if isinstance(__value, (float, int)):
            __value = timedelta(seconds=__value)
        return super().__radd__(__value)

    def __sub__(self, __value: Any) -> Any:
        if isinstance(__value, timedelta):
            return super().__sub__(__value)
        elif isinstance(__value, (float, int)) and __value < _min_timestamps:
            return super().__sub__(timedelta(seconds=__value))
        elif isinstance(__value, (datetime, date, time.struct_time, str, float, int)):
            __value = to_datetime(__value)
            delta = super().__sub__(__value)
            return delta.total_seconds()
        raise TypeError(f"不支持的类型: {type(__value)}")

    def __rsub__(self, __value: Datetime) -> timedelta:
        __value = to_vxdatetime(__value)
        return -self.__sub__(__value)

    @classmethod
    def from_pydatetime(cls, dt: Datetime) -> "VXDatetime":
        """从 datetime 类型转换

        Arguments:
            dt {Datetime} -- 待转换的日期

        Returns:
            VXDatetime -- 转换结果
        """
        if isinstance(dt, VXDatetime):
            return dt

        if isinstance(dt, (date, float, int, str, time.struct_time)):
            date_time: datetime = to_datetime(dt)
        elif isinstance(dt, (datetime)):
            date_time = dt
        else:
            raise ValueError(f"无法转换为 VXDatetime 类型: {dt}")

        return cls(
            year=date_time.year,
            month=date_time.month,
            day=date_time.day,
            hour=date_time.hour,
            minute=date_time.minute,
            second=date_time.second,
            microsecond=date_time.microsecond,
            tzinfo=date_time.tzinfo,
            fold=date_time.fold,
        )

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, (time.struct_time, str, float, int)):
            __value = to_datetime(__value)
            return super().__eq__(__value)
        elif isinstance(__value, (datetime, date, VXDatetime)):
            return super().__eq__(__value)
        return False

    def __ge__(self, __value: Datetime) -> bool:
        __value = to_datetime(__value)
        return super().__ge__(__value)

    def __gt__(self, __value: Datetime) -> bool:
        __value = to_datetime(__value)
        return super().__gt__(__value)

    def __lt__(self, __value: Datetime) -> bool:
        __value = to_datetime(__value)
        return super().__lt__(__value)

    def __le__(self, __value: Datetime) -> bool:
        __value = to_datetime(__value)
        return super().__le__(__value)

    def __hash__(self) -> int:
        return super().__hash__()


VXDatetime.max = VXDatetime.from_pydatetime(datetime.max)
VXDatetime.min = VXDatetime.from_pydatetime(_min_timestamps)


def date_range(
    start: Datetime, end: Datetime, interval: Union[timedelta, float, int]
) -> Generator[VXDatetime, None, None]:
    """生成日期范围

    Arguments:
        start {PYDATETIME} -- 起始日期
        end {PYDATETIME} -- 结束日期
        interval {Union[timedelta, float, int]} -- 间隔

    Returns:
        list[VXDatetime] -- 日期范围
    """
    start = VXDatetime.from_pydatetime(start)
    end = VXDatetime.from_pydatetime(end)
    if start > end:
        raise ValueError("起始日期不能大于结束日期")
    ret = start
    while ret <= end:
        yield ret
        ret += interval


@lru_cache(maxsize=200)
def to_vxdatetime(dt: Datetime) -> VXDatetime:
    """转换为 VXDatetime 类型

    Arguments:
        dt {Datetime} -- 待转换的日期

    Returns:
        VXDatetime -- 转换结果
    """
    return VXDatetime.from_pydatetime(dt)


class VXCalendar:

    def __init__(
        self,
        start_date: Datetime = "2005-01-01",
        end_date: Optional[Datetime] = None,
        special_holidays: Optional[Sequence[Datetime]] = None,
        skip_weekend: bool = True,
    ) -> None:
        self.start_date = to_datetime(start_date)
        self.end_date = (
            to_datetime(end_date)
            if end_date is not None
            else date.today().replace(month=12, day=31)
        )
        if special_holidays is None:
            special_holidays = []
        self._special_holidays = set(
            map(lambda x: to_datetime(x).date(), special_holidays)
        )
        self._trade_dates = (
            pl.DataFrame()
            .with_columns(
                pl.date_range(self.start_date, self.end_date, interval="1d")
                .cast(pl.Date)
                .alias("trade_date"),
            )
            .select(
                [
                    pl.col("trade_date"),
                    pl.when(
                        pl.col("trade_date").dt.weekday().is_in([6, 7]),
                    )
                    .then(not skip_weekend)
                    .when(pl.col("trade_date").is_in(self._special_holidays))
                    .then(0)
                    .otherwise(1)
                    .alias("is_trade_day"),
                ]
            )
        )

    def get_trade_dates(
        self, start: Datetime, end: Datetime, *, closed: bool = True
    ) -> pl.DataFrame:
        """获取交易日历"""
        start = to_datetime(start)
        end = to_datetime(end)
        return (
            self._trade_dates.filter(
                [pl.col("trade_date") >= start, pl.col("trade_date") <= end]
            )
            if closed
            else self._trade_dates.filter(
                [pl.col("trade_date") > start, pl.col("trade_date") < end]
            )
        )

    def add_special_holidays(self, holidays: Sequence[Datetime]) -> None:
        """添加特殊节假日"""
        _holidays = list(map(lambda x: to_datetime(x).date(), holidays))
        self._special_holidays.update(_holidays)

        self._trade_dates = self._trade_dates.with_columns(
            [
                pl.when(
                    pl.col("trade_date").is_in(_holidays),
                )
                .then(0)
                .otherwise(pl.col("is_trade_day"))
                .alias("is_trade_day"),
            ]
        )

    def get_n_day_of_month(self, year: int, month: int, n: int = 1) -> date:
        """获取月份天数"""
        _, last = calendar.monthrange(year, month)
        start = date(year, month, 1)
        end = date(year, month, last)
        n = n - 1 if n > 0 else n
        month_trade_dates = self._trade_dates.filter(
            [
                pl.col("trade_date") >= start,
                pl.col("trade_date") <= end,
                pl.col("is_trade_day") == 1,
            ]
        )["trade_date"]

        return (
            month_trade_dates[-1]
            if n > len(month_trade_dates)
            else month_trade_dates[n]
        )

    def is_trade_day(self, dt: Datetime) -> bool:
        """是否交易日"""
        dt = to_datetime(dt).date()
        return (
            self._trade_dates.filter([pl.col("trade_date") == dt])["is_trade_day"][0]
            == 1
        )

    def get_next_n_day(self, dt: Optional[Datetime] = None, n: int = 1) -> date:
        """获取下N个交易日"""
        if dt is None:
            dt = date.today()
        else:
            dt = to_datetime(dt).date()
        trade_dates = self._trade_dates.filter(
            [pl.col("trade_date") > dt, pl.col("is_trade_day") == 1]
        )["trade_date"]
        return trade_dates[n - 1]

    def get_previous_n_day(self, dt: Optional[Datetime] = None, n: int = 1) -> date:
        """获取前N个交易日"""
        if dt is None:
            dt = date.today()
        else:
            dt = to_datetime(dt).date()
        trade_dates = self._trade_dates.filter(
            [pl.col("trade_date") < dt, pl.col("is_trade_day") == 1]
        )["trade_date"]
        return trade_dates[-n]


if __name__ == "__main__":
    dt1 = VXDatetime(2023, 1, 2)
    print(dt1)
    print(VXDatetime.today(timestr="12:34:56") + 4)
    print(4 + VXDatetime.today(timestr="12:34:56"))
    print(VXDatetime.from_pydatetime("2023-01-02 12:34:56"))
    print(VXDatetime.from_pydatetime(1641107696.0))

    print(dt1 - 3)
    print(time.time() - dt1)
    dt2 = dt1.timestamp()
    print(dt1 == dt2)
    dt3 = dt1.date()
    print(dt1 == dt3)
    print(dt1 == str(dt1))
    print(dt1 > dt1 + 3)
    print("2023-01-02 12:34:56" > dt1 - 3)
    print(dt1.timestamp() > dt1 - 3)
    print(hash(dt1))
    print(hash(dt1 + 3))
    # for i in date_range("2023-01-01", "2023-01-3", 30 * 60):
    #    print(i)
    print(VXDatetime.now(), VXDatetime.now() + 1, VXDatetime.now() - 1)
