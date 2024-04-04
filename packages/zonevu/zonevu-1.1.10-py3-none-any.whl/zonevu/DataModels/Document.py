from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase
from strenum import StrEnum
from pathlib import Path
from .DataModel import DataObjectTypeEnum


class DocumentTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Other = 'Other'
    ObserverNotes = 'ObserverNotes'
    LoadSheet = 'LoadSheet'
    ProcessingNotes = 'ProcessingNotes'
    ProjectBid = 'ProjectBid'
    SurveyPlat = 'SurveyPlat'
    Contract = 'Contract'
    DrillingReport = 'DrillingReport'
    DrillingDiagram = 'DrillingDiagram'
    DrillingPlan = 'DrillingPlan'
    AFE = 'AFE'
    JointOperatingAgreement = 'JointOperatingAgreement'
    DivisionOrder = 'DivisionOrder'
    RevenueStatement = 'RevenueStatement'
    JointInterestBill = 'JointInterestBill'
    OperatingInvoice = 'OperatingInvoice'
    RoyaltyStatement = 'RoyaltyStatement'
    GasBalancingStatement = 'GasBalancingStatement'
    CrudeOilRunTicket = 'CrudeOilRunTicket'
    LeaseOperatingStatement = 'LeaseOperatingStatement'
    Regulatory = 'Regulatory'
    EnvironmentalImpactStatement = 'EnvironmentalImpactStatement'
    Presentation = 'Presentation'
    Permit = 'Permit'


class ActivityTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Acquisition = 'Acquisition'
    Exploration = 'Exploration'
    Drilling = 'Drilling'
    Completion = 'Completion'
    Production = 'Production'
    Recompletion = 'Recompletion'
    Abandonment = 'Abandonment'


class DisciplineTypeEnum(StrEnum):
    Unknown = 'Unknown'
    Engineering = 'Engineering'
    Geoscience = 'Geoscience'
    Land = 'Land'
    Accounting = 'Accounting'
    Legal = 'Legal'
    Corporate = 'Corporate'
    Marketing = 'Marketing'
    Drilling = 'Drilling'
    Completions = 'Completions'
    Geosteering = 'Geosteering'


class ConfidenceTypeEnum(StrEnum):
    Unknown = 'Unknown'
    High = 'High'
    Medium = 'Medium'
    Low = 'Low'


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class Document:
    """
    Represents a catalog entry for a document that exists in the Documents folder of a data folder in ZoneVu
    Wells, Seismic surveys, Projects, and Geomodels have data folders with a Document root folder.
    NOTE: the path field should be a relative path starting with 'Documents' that includes the filename and extension
    For example:  Documents/Contracts/JOA.doc
    """
    id: int = -1                    #: System id of document entry in catalog
    row_version: Optional[str] = None
    name: Optional[str] = None       #: The file name and extension of the document
    file_size: int = 0               #: Size of document file in bytes
    description: Optional[str] = None
    owner_type: DataObjectTypeEnum = DataObjectTypeEnum.Unknown  # System type of owner data entity.
    owner_id: int = -1              #: System id of owning data entity (Well, Seismic Survey, Project, GeoModel)
    path: str = ''                  #: A relative path within Document folder of the owning data entity
    author: Optional[str] = None
    document_type: DocumentTypeEnum = DocumentTypeEnum.Unknown
    activity: ActivityTypeEnum = ActivityTypeEnum.Unknown
    discipline: DisciplineTypeEnum = DisciplineTypeEnum.Unknown
    confidence: ConfidenceTypeEnum = ConfidenceTypeEnum.Unknown

    def is_valid(self) -> bool:
        path_str = str(self.path)
        has_doc_root = str(self.path).startswith('Documents')
        file_names_match = self.name == Path(self.path).name == self.name
        has_owner = self.owner_id > 0 and self.owner_type != DataObjectTypeEnum.Unknown
        file_real = self.file_size > 0
        valid = has_doc_root and file_names_match and has_owner and file_real
        return valid

    def set_path(self, file_name: str, relative_path: str = ''):
        """
        Convenience method to set the document path for storing of the file in the data folder
        :param file_name: The file name and extension, e.g. contract.doc
        :param relative_path: relative path to subdirectory for store file, or empty string.
        """
        actual_path = Path('Documents') / relative_path / file_name
        self.path = str(actual_path)

