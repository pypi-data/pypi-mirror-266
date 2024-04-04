from typing import Optional, ClassVar, List
from dataclasses import dataclass, field
from ..DataModel import DataModel
from ..PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from ..Document import Document
from pathlib import Path
from ...Services.Storage import Storage
from strenum import StrEnum


class ZDomainEnum(StrEnum):
    Time = 'Time'
    Depth = 'Depth'
    Velocity = 'Velocity'
    Amplitude = 'Amplitude'


@dataclass
class Volume(DataModel):
    description: Optional[str] = None
    vintage: Optional[str] = None   # Processing vintage
    domain: ZDomainEnum = ZDomainEnum.Depth
    area: float = 0   # Area on ground
    header: str = ''  # SEGY text Header
    size: int = 0   # Size of seismic volume in megabytes
    segy_filename: Optional[str] = None


@dataclass
class SeismicSurvey(PrimaryDataObject):
    # Represents a ZoneVu seismic survey  Object
    division_id: int = 0
    division: str = ''
    number: Optional[str] = None
    type: str = ''
    description: Optional[str] = None
    row_version: Optional[str] = None
    num_datasets: int = 0
    documents: List[Document] = field(default_factory=list[Document])
    seismic_volumes: List[Volume] = field(default_factory=list[Volume])

    archive_dir_name: ClassVar[str] = 'seismicsurveys'
    archive_json_filename: ClassVar[str] = 'seismicsurvey.json'

    @property
    def full_name(self) -> str:
        return self.name

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.SeismicSurvey

    @property
    def archive_local_dir_path(self) -> Path:
        return Path(self.archive_dir_name) / self.safe_name

    @property
    def archive_local_file_path(self) -> Path:
        return self.archive_local_dir_path / self.archive_json_filename

    def save(self, storage: Storage) -> None:
        super().save(storage)

    @classmethod
    def retrieve(cls, dir_path: Path, storage: Storage) -> 'SeismicSurvey':
        seismic_json_path = dir_path / cls.archive_json_filename
        json_obj = PrimaryDataObject.retrieve_json(seismic_json_path, storage)
        seismic = cls.from_dict(json_obj)
        return seismic


@dataclass
class SeismicSurveyEntry(DataModel):
    # Represents a ZoneVu seismic survey catalog entry Object (lightweight)
    division_id: int = 0
    division: str = ''
    number: Optional[str] = None
    type: str = ''
    description: Optional[str] = None
    row_version: Optional[str] = None
    num_datasets: int = 0

    @property
    def seismic_survey(self) -> SeismicSurvey:
        return SeismicSurvey(id=self.id, name=self.name, row_version=self.row_version, description=self.description,
                             division=self.division, division_id=self.division_id, number=self.number,
                             num_datasets=self.num_datasets, type=self.type)
