from ..DataModel import DataModel
from dataclasses import dataclass
from typing import Optional, ClassVar
from strenum import StrEnum


@dataclass
class Plug(DataModel):
    description: Optional[str] = None
    sequence_num: int = -1
    toe_md: Optional[float] = None
    heel_md: float = 0
