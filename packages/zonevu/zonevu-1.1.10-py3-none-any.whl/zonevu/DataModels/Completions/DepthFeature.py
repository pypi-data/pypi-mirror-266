from ..DataModel import DataModel
from dataclasses import dataclass
from typing import Optional, ClassVar
from strenum import StrEnum


class DepthFeatureKindEnum(StrEnum):
    Undefined = 'Undefined'
    Plug = 'Plug'
    Perforation = 'Perforation'


@dataclass
class DepthFeature(DataModel):
    stage_name: int = -1
    kind: DepthFeatureKindEnum = DepthFeatureKindEnum.Undefined
    top_md: float = 0
    bottom_md: float = 0
    shot_density: Optional[int] = None
    shot_count: Optional[int] = None
    phasing: Optional[float] = None
    orientation: Optional[float] = None
