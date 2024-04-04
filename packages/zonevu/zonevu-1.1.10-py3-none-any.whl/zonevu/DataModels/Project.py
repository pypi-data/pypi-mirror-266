from typing import Optional, ClassVar, List
from dataclasses import dataclass, field
from dataclasses_json import config
from .DataModel import DataModel, ChangeAgentEnum
from .PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from .Map.UserLayer import UserLayer
from .Document import Document
from ..Services.Storage import Storage
from strenum import PascalCaseStrEnum
from enum import auto
from datetime import datetime
from pathlib import Path
from .Helpers import MakeIsodataOptionalField
from ..DataModels.Wells.Well import WellEntry
from ..DataModels.Geospatial.Crs import CrsSpec
from ..DataModels.Seismic.SeismicSurvey import SeismicSurveyEntry
from ..DataModels.Geomodels.Geomodel import GeomodelEntry
from .Geospatial.Crs import DistanceUnitsEnum


class ProjectTypeEnum(PascalCaseStrEnum):
    Unspecified = auto()
    Prospect = auto()
    AreaOfInterest = auto()
    Development = auto()
    Operations = auto()
    Job = auto()
    Subscription = auto()
    DealRoom = auto()
    DataRoom = auto()
    SeismicSurvey = auto()
    Well = auto()
    Pad = auto()


@dataclass
class Project(PrimaryDataObject):
    """
    ZoneVu project
    """
    #: System id of corporate division of project
    division_id: int = 0
    #: Name of corporate division of project
    division: str = ''
    #: Mandatory CRS
    coordinate_system: Optional[CrsSpec] = None
    number: Optional[str] = None
    description: Optional[str] = None
    project_type: ProjectTypeEnum = ProjectTypeEnum.Unspecified
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    creator: Optional[str] = None
    change_agent: ChangeAgentEnum = ChangeAgentEnum.Unknown
    creation_date: Optional[datetime] = MakeIsodataOptionalField()
    last_modified_date: Optional[datetime] = MakeIsodataOptionalField()
    property_number: Optional[str] = None
    afe_number: Optional[str] = None
    basin: Optional[str] = None
    play: Optional[str] = None
    zone: Optional[str] = None
    producing_field: Optional[str] = field(default=None, metadata=config(field_name="Field"))
    country: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    district: Optional[str] = None
    block: Optional[str] = None
    is_active: bool = False
    is_complete: bool = False
    is_confidential: bool = False
    start_date: Optional[datetime] = MakeIsodataOptionalField()
    completion_date: Optional[datetime] = MakeIsodataOptionalField()
    confidential_release_date: Optional[datetime] = MakeIsodataOptionalField()
    strat_column_id: Optional[int] = None
    strat_column_name: Optional[str] = None
    wells: List[WellEntry] = field(default_factory=list[WellEntry])
    layers: List[UserLayer] = field(default_factory=list[UserLayer])
    documents: List[Document] = field(default_factory=list[Document])
    seismic_surveys: List[SeismicSurveyEntry] = field(default_factory=list[SeismicSurveyEntry])
    geomodel: Optional[GeomodelEntry] = None

    archive_dir_name: ClassVar[str] = 'projects'
    archive_json_filename: ClassVar[str] = 'project.json'

    @property
    def full_name(self) -> str:
        return self.name

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.Project

    @property
    def archive_local_dir_path(self) -> Path:
        return Path(self.archive_dir_name) / self.safe_name

    @property
    def archive_local_file_path(self) -> Path:
        return self.archive_local_dir_path / self.archive_json_filename

    def save(self, storage: Storage) -> None:
        super().save(storage)

        # Give change for specialized items to be written.
        for layer in self.layers:
            layer.save(self.archive_local_dir_path, storage)

    @classmethod
    def retrieve(cls, dir_path: Path, storage: Storage) -> 'Project':
        project_json_path = dir_path / cls.archive_json_filename
        json_obj = PrimaryDataObject.retrieve_json(project_json_path, storage)
        project = cls.from_dict(json_obj)

        # Give change for specialized items to be read.
        for layer in project.layers:
            layer.retrieve(dir_path, storage)

        return project


@dataclass
class ProjectEntry(DataModel):
    # Represents a ZoneVu Project catalog entry Object (lightweight)
    division_id: int = 0
    division: str = ''
    number: Optional[str] = None
    description: Optional[str] = None
    row_version: Optional[str] = None

    @property
    def project(self) -> Project:
        return Project(id=self.id, name=self.name, row_version=self.row_version, description=self.description,
                       division=self.division, division_id=self.division_id, number=self.number)
