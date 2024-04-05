import dataclasses
from typing import Optional, Union, ClassVar, List
from dataclasses import dataclass, field
from datetime import datetime
from ...DataModels.Wells.Wellbore import Wellbore
from ...DataModels.Document import Document
from dataclasses_json import config
from strenum import StrEnum, PascalCaseStrEnum
from enum import auto
import copy
from pathlib import Path
from ...DataModels.Helpers import MakeIsodataOptionalField
from ...DataModels.DataModel import DataModel, ChangeAgentEnum, WellElevationUnitsEnum
from ...DataModels.PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from ...Services.Storage import Storage


class WellElevationTypeEnum(StrEnum):
    KB = 'KB'
    Wellhead = 'Wellhead'
    Ground = 'Ground'
    Water = 'Water'


class WellDirectionEnum(StrEnum):
    Unknown = 'Unknown'
    HuffNPuff = 'HuffNPuff'
    Injector = 'Injector'
    Producer = 'Producer'
    Uncertain = 'Uncertain'


class WellPurposeEnum(StrEnum):
    Unknown = 'Unknown'
    Appraisal = 'Appraisal'
    Appraisal_Confirmation = 'Appraisal_Confirmation'
    Appraisal_Exploratory = 'Appraisal_Exploratory'
    Exploration = 'Exploration'
    Exploration_DeeperPoolWildcat = 'Exploration_DeeperPoolWildcat'
    Exploration_NewFieldWildcat = 'Exploration_NewFieldWildcat'
    Exploration_NewPoolWildcat = 'Exploration_NewPoolWildcat'
    Exploration_OutpostWildcat = 'Exploration_OutpostWildcat'
    Exploration_ShallowerPoolWildcat = 'Exploration_ShallowerPoolWildcat'
    Development = 'Development'
    Development_InfillDevelopment = 'Development_InfillDevelopment'
    Development_Injector = 'Development_Injector'
    Development_Producer = 'Development_Producer'
    FluidStorage = 'FluidStorage'
    FluidStorage_Gas = 'FluidStorage_Gas'
    GeneralServices = 'GeneralServices'
    GeneralServices_BoreholeReacquisition = 'GeneralServices_BoreholeReacquisition'
    GeneralServices_Observation = 'GeneralServices_Observation'
    GeneralServices_Relief = 'GeneralServices_Relief'
    GeneralServices_Research = 'GeneralServices_Research'
    GeneralServices_Research_DrillTest = 'GeneralServices_Research_DrillTest'
    GeneralServices_Research_StratTest = 'GeneralServices_Research_StratTest'
    Mineral = 'Mineral'


class WellFluidEnum(StrEnum):
    Unknown = 'Unknown'
    Air = 'Air'
    Condensate = 'Condensate'
    Dry = 'Dry'
    Gas = 'Gas'
    Gas_Water = 'Gas_Water'
    Non_Hydrocarbon_Gas = 'Non_Hydrocarbon_Gas'
    Non_Hydrocarbon_Gas_CO2 = 'Non_Hydrocarbon_Gas_CO2'
    Oil = 'Oil'
    Oil_Gas = 'Oil_Gas'
    Oil_Water = 'Oil_Water'
    Steam = 'Steam'
    Water = 'Water'
    Water_Brine = 'Water_Brine'
    Water_FreshWater = 'Water_FreshWater'


class EnvironmentTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Land = 'Land'
    Marine = 'Marine'
    Transition = 'Transition'


class WellStatusEnum(PascalCaseStrEnum):
    Unknown = auto()
    Active = auto()
    ActiveInjecting = auto()
    ActiveProducing = auto()
    Completed = auto()
    Drilling = auto()
    PartiallyPlugged = auto()
    Permitted = auto()
    PluggedAndAbandoned = auto()
    Proposed = auto()
    Sold = auto()
    Suspended = auto()
    TemporarilyAbandoned = auto()
    Testing = auto()
    Tight = auto()
    WorkingOver = auto()


@dataclass
class Well(PrimaryDataObject):
    """
    Represents a ZoneVu Well Object
    """
    external_id: Optional[str] = None
    external_source: Optional[str] = None
    creator: Optional[str] = None
    change_agent: ChangeAgentEnum = ChangeAgentEnum.Unknown
    creation_date: Optional[datetime] = MakeIsodataOptionalField()
    last_modified_date: Optional[datetime] = MakeIsodataOptionalField()
    operator: Optional[str] = None
    number: Optional[str] = None
    description: Optional[str] = None
    uwi: Optional[str] = field(default=None, metadata=config(field_name="UWI"))
    original_uwi: Optional[str] = None
    division: Optional[str] = None
    division_id: Optional[int] = None
    status: Optional[WellStatusEnum] = WellStatusEnum.Unknown
    environment: Optional[EnvironmentTypeEnum] = EnvironmentTypeEnum.Unknown
    purpose: Optional[WellPurposeEnum] = WellPurposeEnum.Unknown
    fluid_type: Optional[WellFluidEnum] = WellFluidEnum.Unknown
    well_direction: Optional[WellDirectionEnum] = WellDirectionEnum.Unknown
    property_number: Optional[str] = None
    afe_number: Optional[str] = field(default=None, metadata=config(field_name="AFENumber"))
    spud_date: Optional[datetime] = MakeIsodataOptionalField()
    completion_date: Optional[datetime] = MakeIsodataOptionalField()
    target_zone: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    basin: Optional[str] = None
    play: Optional[str] = None
    zone: Optional[str] = None
    field: Optional[str] = None
    country: Optional[str] = None
    state: Optional[str] = None
    county: Optional[str] = None
    elevation: Optional[float] = None
    elevation_type: Optional[WellElevationTypeEnum] = WellElevationTypeEnum.KB
    elevation_units: Optional[WellElevationUnitsEnum] = None
    target_zone_id: Optional[int] = None
    location_datum: Optional[str] = None
    strat_column_id: Optional[int] = None
    azimuth: Optional[float] = None
    wellbores: List[Wellbore] = dataclasses.field(default_factory=list[Wellbore])
    documents: List[Document] = dataclasses.field(default_factory=list[Document])

    archive_dir_name: ClassVar[str] = 'wells'
    archive_json_filename: ClassVar[str] = 'well.json'

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.Well

    def init_primary_wellbore(self):
        primary_wellbore = Wellbore()
        primary_wellbore.name = 'Primary'
        self.wellbores = []
        self.wellbores.append(primary_wellbore)

    def copy_ids_from(self, source: 'DataModel'):
        super().copy_ids_from(source)
        # well: Well = cast(Well, source)
        if isinstance(source, Well):
            DataModel.merge_lists(self.wellbores, source.wellbores)

    def make_trimmed_copy(self) -> 'Well':
        # Make a copy that is suitable for creating wells through the Web API
        wellbores = self.wellbores
        self.wellbores = []
        well_copy = copy.deepcopy(self)
        well_copy.wellbores = [bore.make_trimmed_copy() for bore in wellbores]
        self.wellbores = wellbores
        return well_copy

    def get_documents(self) -> List[Document]:
        return self.documents

    @property
    def full_name(self) -> str:
        if self.number is None:
            return self.name or 'unnamed'
        else:
            return '%s %s' % (self.name, self.number)

    @property
    def primary_wellbore(self) -> Union[Wellbore, None]:
        """
        Gets the primary wellbore on the well. Normally, there is only a wellbore per well,
        and it is the primary wellbore
        """
        return self.wellbores[0] if len(self.wellbores) > 0 else None

    # region Support for saving wells to files and to cloud storage
    @property
    def archive_local_dir_path(self) -> Path:
        """
        Within a file or cloud archive, the directory path for this well
        Example: Archive dir for 'Smith A-1' is 'wells/smith-a-1'
        :return:
        """
        return Path(self.archive_dir_name) / self.safe_name

    @property
    def archive_local_file_path(self) -> Path:
        """
        Within a file or cloud archive, the file path for the serialized json for this well
        Example: Example: Archive file path for 'Smith A-1' is 'wells/smith-a-1/well.json'
        :return:
        """
        return self.archive_local_dir_path / self.archive_json_filename

    def save(self, storage: Storage):
        """
        Serialize a well data and store in user storage under a local path.
        Example: for the 'Smith A-1' well, the local path in user storage is 'wells/smith-a-1/well.json'.
        NOTE: also passes along the row version of the well as a tag.
        :param storage: a user file based or cloud storage service
        :return:
        """
        super().save(storage)

        # Give change for specialized items to be written.
        for wellbore in self.wellbores:
            wellbore.save(self.archive_local_dir_path, storage)

    @classmethod
    def retrieve(cls, dir_path: Path, storage: Storage) -> 'Well':
        """
        Retrieve well data from user storage and deserialize into a well instance.
        :param dir_path: folder local path containing the well.json file (e.g. wells/smith-a-1-3568)
        :param storage: a user file based or cloud storage service
        :return:
        """
        well_json_path = dir_path / cls.archive_json_filename
        json_obj = PrimaryDataObject.retrieve_json(well_json_path, storage)
        well = cls.from_dict(json_obj)

        # Give change for specialized items to be read.
        for wellbore in well.wellbores:
            wellbore.retrieve(dir_path, storage)

        return well
    # endregion


@dataclass
class WellEntry(DataModel):
    # Represents a ZoneVu Well catalog entry Object (lightweight)
    id: int = -1
    uwi: Optional[str] = None
    name: str = ''
    number: Optional[str] = None
    description: Optional[str] = None
    division: Optional[str] = None
    division_id: Optional[int] = None
    status: Optional[str] = None

    @property
    def full_name(self):
        if self.number is None:
            return self.name or 'unnamed'
        else:
            return '%s %s' % (self.name, self.number)

    @property
    def well(self) -> Well:
        return Well(id=self.id, name=self.name, row_version=self.row_version, number=self.number,
                    description=self.description, division=self.division, division_id=self.division_id,
                    status=self.status)







