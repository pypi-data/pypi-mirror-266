from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase, config, DataClassJsonMixin
from .Enums import DistanceUnitsEnum


# Projected coordinate system specification
# @dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CrsSpec(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    """
    Used to specify a projected coordinate system
    The EPSG code takes preference if both are specified.
    The Units data member if provided overrides the default units of the specified coordinate system
    """
    epsg_code: Optional[int] = None
    projection: Optional[str] = None       # DotSpatial string for projection
    zone: Optional[str] = None              # DotSpatial string for zone
    units: Optional[DistanceUnitsEnum] = DistanceUnitsEnum.Undefined         # Distance units override.

    @classmethod
    def from_epsg_code(cls, code: int, units: DistanceUnitsEnum = DistanceUnitsEnum.Undefined) -> 'CrsSpec':
        return cls(code, None, None, units)

    @classmethod
    def from_names(cls, projection: str, zone: str, units: DistanceUnitsEnum = DistanceUnitsEnum.Undefined) -> 'CrsSpec':
        return cls(None, projection, zone, units)

    def to_string(self) -> str:
        has_epsg = self.epsg_code != DistanceUnitsEnum.Undefined
        if has_epsg:
            return 'CRS (EPSG=%s, UNITS=%s)' % (self.epsg_code, self.units)
        else:
            return 'CRS (PROJ=%s, ZONE=%s, UNITS=%s)' % (self.projection, self.zone, self.units)


# @dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class CrsEntry(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    id: str        # DotSpatial string for projection
    name: str              # DotSpatial string for zone



