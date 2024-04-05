from ..DataModel import DataModel
from dataclasses import dataclass
from typing import Optional, ClassVar
from strenum import StrEnum


class FracTypeEnum(StrEnum):
    Plan = 'Plan'
    Actual = 'Actual'


@dataclass
class FracEntry(DataModel):
    """
    Represents a ZoneVu catalog entry for a frac on a wellbore
    """
    #: Description of the frac
    description: Optional[str] = None
    #: Frac type
    frac_type: FracTypeEnum = FracTypeEnum.Actual
