from datetime import datetime
from strenum import StrEnum
from typing import Union
from dataclasses import field
from dataclasses_json import config
from marshmallow import fields


def iso_to_datetime(value: Union[str, None]) -> Union[datetime, None]:
    """
    Parser for parsing ISO times strings to python datetime
    :param value:
    :return:
    """
    if value is None:
        return None
    try:
        date = datetime.fromisoformat(value)
        return date
    except TypeError:
        return None
    except ValueError:
        return None


def date_time_to_iso(value: Union[datetime, None]) -> Union[str, None]:
    """
    Converts python datetime to ISO string
    :param value:
    :return:
    """
    if value is None:
        return None
    return value.isoformat()


isodateFieldConfig = config(
    encoder=date_time_to_iso,
    decoder=iso_to_datetime,
    mm_field=fields.DateTime(format='iso')
)
isodateFieldConfigHide = {
    "encoder": lambda dt: dt.isoformat(),
    "decoder": lambda dt_str: datetime.fromisoformat(dt_str),
}
isodateOptional = field(default=None, metadata=isodateFieldConfig)


def MakeIsodataOptionalField():
    return field(default=None, metadata=isodateFieldConfig)


class DepthUnitsEnum(StrEnum):
    """
    Enum of ZoneVu depth units
    """
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'



