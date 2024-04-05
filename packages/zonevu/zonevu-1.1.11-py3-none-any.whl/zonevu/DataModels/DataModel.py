from typing import Optional, TypeVar, List
from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
from strenum import StrEnum


class DataObjectTypeEnum(StrEnum):
    SeismicSurvey = 'SeismicSurvey'
    Well = 'Well'
    Project = 'Project'
    Geomodel = 'Geomodel'
    StratColumn = 'StratColumn'
    Unknown = 'Unknown'


class ChangeAgentEnum(StrEnum):
    Unknown = 'Unknown'
    GuiCreate = 'GuiCreate'
    GuiImport = 'GuiImport'
    GuiBulkImport = 'GuiBulkImport'
    WebApi = 'WebApi'


class WellElevationUnitsEnum(StrEnum):
    Undefined = 'Undefined'
    Meters = 'Meters'
    Feet = 'Feet'
    FeetUS = 'FeetUS'


T = TypeVar("T", bound='DataModel')


@dataclass
class DataModel(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    #: System id of this data object
    id: int = -1
    #: Row version for tracking changes on this data object
    row_version: Optional[str] = None
    #: Data object name
    name: Optional[str] = None

    def merge_from(self, source: 'DataModel'):
        self.__dict__.update(source.__dict__)

    def copy_ids_from(self, source: 'DataModel'):
        self.id = source.id

    @staticmethod
    def merge_lists(dst_list: List[T], src_list: List[T]):
        for (dst, src) in zip(dst_list, src_list):
            if dst is not None and src is not None:
                dst.copy_ids_from(src)




