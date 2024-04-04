from typing import Optional
from dataclasses import dataclass
from ...DataModels.DataModel import DataModel
from strenum import StrEnum, PascalCaseStrEnum


class GeoPeriodEnum(StrEnum):
    Unset = 'Unset',
    Quaternary = 'Quaternary',
    Neogene = 'Neogene',
    Paleogene = 'Paleogene',
    Cretaceous = 'Cretaceous',
    Jurassic = 'Jurassic',
    Triassic = 'Triassic',
    Permian = 'Permian',
    Carboniferous = 'Carboniferous',
    Devonian = 'Devonian',
    Silurian = 'Silurian',
    Ordovician = 'Ordovician',
    Cambrian = 'Cambrian',
    Precambrian = 'Precambrian'


class LithologyTypeEnum(PascalCaseStrEnum):
    Unset = 'Unset',
    Sandstone = 'Sandstone',
    Shale = 'Shale',
    Limestone = 'Limestone',
    Dolomite = 'Dolomite',
    Chalk = 'Chalk',
    Marl = 'Marl',
    MudstoneRich = 'MudstoneRich',
    MudstoneLean = 'MudstoneLean',
    Bentonite = 'Bentonite',
    Coal = 'Coal',
    Chert = 'Chert',
    Anhydrite = 'Anhydrite',
    Siltstone = 'Siltstone',
    ShalySand = 'ShalySand',
    SandstoneBedded = 'SandstoneBedded',
    CalcareousSandstone = 'CalcareousSandstone',
    SandyShale = 'SandyShale',
    ShalyLimestone = 'ShalyLimestone',
    SandyLimestone = 'SandyLimestone',
    ShalyDolostone = 'ShalyDolostone',
    SandyDolostone = 'SandyDolostone',
    LimestoneShale = 'LimestoneShale',
    ShaleSandstone = 'ShaleSandstone',
    SandstoneShale = 'SandstoneShale',
    ShaleLimestone = 'ShaleLimestone',
    Salt = 'Salt',
    ChertyShale = 'ChertyShale',
    Breccia = 'Breccia',
    Conglomerate = 'Conglomerate',
    Basalt = 'Basalt',
    Granite = 'Granite',
    Igneous = 'Igneous',
    Tuff = 'Tuff',
    Crosshatch = 'Crosshatch'


@dataclass
class Formation(DataModel):
    """
    A geologic formation
    """
    #: Formation name
    # Note: formation name is the DataModel 'name' data field
    #: Optional column member name
    member_name: Optional[str] = None
    #: Required stratigraphic order ordinal
    strat_col_order: int = -1
    #: Formation symbol (mnemonic)
    symbol: str = ''
    #: Optional default color for rendering this formation in a display
    color: Optional[str] = None
    #: Optional description of formation
    description: Optional[str] = None
    #: Optional geologic age of this formation
    period: Optional[GeoPeriodEnum] = None
    # Optional lithology of this formation
    lithology_type: Optional[LithologyTypeEnum] = None

