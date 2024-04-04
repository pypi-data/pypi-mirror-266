from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import config
from ...DataModels.DataModel import DataModel
from datetime import datetime
from ...DataModels.Helpers import MakeIsodataOptionalField


@dataclass
class Station(DataModel):
    md: float = field(default=0, metadata=config(field_name="MD"))
    tvd: float = field(default=0, metadata=config(field_name="TVD"))
    # md: Optional[float] = field(default=None, metadata=config(field_name="MD"))
    # tvd: Optional[float] = field(default=None, metadata=config(field_name="TVD"))
    inclination: Optional[float] = None
    azimuth: Optional[float] = None
    elevation: Optional[float] = None
    delta_x: Optional[float] = None
    delta_y: Optional[float] = None
    vx: Optional[float] = field(default=None, metadata=config(field_name="VX"))
    time: Optional[datetime] = MakeIsodataOptionalField()


