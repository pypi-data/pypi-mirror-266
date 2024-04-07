"""基础模型"""

import datetime
from typing import Any, Dict
from pydantic import (
    BaseModel,
    Field,
    ConfigDict,
    field_validator,
    PlainValidator,
    TypeAdapter,
)
from vxutils.dtutils import VXDatetime, to_vxdatetime

try:
    from typing import Annotated
except ImportError:
    from typing_extensions import Annotated

DatetimeType = datetime.datetime


class VXDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    updated_dt: VXDatetime = Field(
        default_factory=VXDatetime.now, validate_default=True
    )
    created_dt: DatetimeType = Field(
        default_factory=VXDatetime.now, validate_default=True
    )

    def __init__(self, **data: Dict[str, Any]) -> None:
        created_dt: VXDatetime = data.setdefault("created_dt", VXDatetime.now())
        updated_dt: VXDatetime = data.setdefault("updated_dt", created_dt)

        super().__init__(**data)
        self.__dict__.pop("created_dt", None)
        self.__dict__.pop("updated_dt", None)
        self.created_dt = created_dt
        self.updated_dt = updated_dt

    def __setattr__(self, name: str, value: Any) -> None:
        field_info = self.model_fields.get(name)
        if field_info and field_info.annotation != type(value) and field_info.metadata:
            value = TypeAdapter(field_info.annotation).validate_python(value)

        if name not in ["updated_dt", "created_dt"]:
            self.updated_dt = VXDatetime.now()
        return super().__setattr__(name, value)

    def __str__(self) -> str:
        return self.model_dump_json(indent=4)

    def __repr__(self) -> str:
        return self.model_dump_json(indent=4)

    @field_validator("updated_dt", "created_dt", mode="plain")
    def validate_datetime(cls, value: Any) -> VXDatetime:
        return to_vxdatetime(value)


if __name__ == "__main__":
    from pprint import pprint

    class vxTick(VXDataModel):
        symbol: str
        trigger_dt: Annotated[datetime.datetime, PlainValidator(to_vxdatetime)] = Field(
            default_factory=datetime.datetime.now
        )

    tick = vxTick(symbol="123")
    pprint(tick.__pydantic_core_schema__)
    tick.updated_dt = "2021-01-01 00:00:00"
    tick.trigger_dt = "2021-01-01 00:00:00"
    pprint(tick.model_fields)

    print(tick)
    print(type(tick.updated_dt))
    print(type(tick.trigger_dt))
