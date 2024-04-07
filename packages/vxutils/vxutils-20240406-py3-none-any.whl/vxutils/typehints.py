""""""

import sys
import time
from datetime import datetime, date
from typing import Union
from pydantic import Field

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

__all__ = ["Timestamp", "Datetime"]

_min_timestamps = datetime(1980, 1, 1).timestamp()
Timestamp = Annotated[Union[float, int], Field(gt=_min_timestamps)]
Datetime = Union[datetime, date, Timestamp, str, time.struct_time]
