from strenum import StrEnum
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, LetterCase, config, DataClassJsonMixin
from typing import Optional
from ...DataModels.Geospatial.Enums import DistanceUnitsEnum
from ...DataModels.Geospatial.Crs import CrsSpec


class EndianOrderEnum(StrEnum):
    BigEndian = 'BigEndian'
    LittleEndian = 'LittleEndian'


class SegyRevisionEnum(StrEnum):
    Rev0 = 'Rev0'
    Rev1 = 'Rev1'
    Rev2 = 'Rev2'


class SampleFormatEnum(StrEnum):
    Undefined = 'Undefined'
    IbmFloat = 'IbmFloat'
    IeeeFloat = 'IeeeFloat'
    Int4 = 'Int4'
    Int2 = 'Int2'
    Int1 = 'Int1'


class TextFormatEnum(StrEnum):
    Ebcdic = 'Ebcdic'
    Ascii = 'Ascii'


class ZDomainEnum(StrEnum):
    Time = 'Time'
    Depth = 'Depth'
    Velocity = 'Velocity'
    Amplitude = 'Amplitude'


class SampleIntervalUnitsEnum(StrEnum):
    Undefined = 'Undefined'
    Millisecs = 'Millisecs'
    Feet = 'Feet'
    Meters = 'Meters'


class LineOrderEnum(StrEnum):
    InlineOrder = 'InlineOrder'
    CrosslineOrder = 'CrosslineOrder'
    SliceOrder = 'SliceOrder'
    Bricked = 'Bricked'
    Unknown = 'Unknown'


@dataclass
class DatumSpec(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    elevation: Optional[float] = None
    replacement_velocity: Optional[float] = None
    depth_units: DistanceUnitsEnum = DistanceUnitsEnum.Undefined


@dataclass
class TraceInfo(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    fixed_length_traces: bool = True
    num_samples: int = 0
    sample_interval: int = 0        # In microseconds, feet, or meters
    sample_interval_r: float = 0    # Calculated sample interval - SampleInterval / SampleIntervalDivisor  Always either millisecs, feet, or meters.
    sample_interval_units: SampleIntervalUnitsEnum = SampleIntervalUnitsEnum.Undefined
    start_time: float = 0       # Start time of first sample in millisecs, feet, or meters.


@dataclass
class SegyFormatInfo(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    revision: SegyRevisionEnum = SegyRevisionEnum.Rev0
    endian_order: EndianOrderEnum = EndianOrderEnum.LittleEndian
    line_order: LineOrderEnum = LineOrderEnum.InlineOrder
    sample_format: SampleFormatEnum = SampleFormatEnum.IbmFloat
    distance_units: DistanceUnitsEnum = DistanceUnitsEnum.Undefined
    num_samples: int = 0
    sample_interval: int = 0        # X1000
    file_size: int = 0
    text_format: TextFormatEnum = TextFormatEnum.Ascii
    num_extended_text_headers: int = 0
    fixed_length_traces: bool = True
    upload_block_size: int = 0
    inline_byte_position: int = 0
    crossline_byte_position: int = 0
    x_coord_byte_position: int = 0
    y_coord_byte_position: int = 0
    coord_scalar_byte_position: int = 0
    coord_scalar_override: Optional[float] = None


@dataclass
class SeismicInfo(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    survey_name: str
    volume_name: str
    volume_id: int
    segy_filename: str
    domain: ZDomainEnum
    datum: DatumSpec
    coordinate_system: CrsSpec
    trace_info: TraceInfo
    is_segy_registered: bool
    segy_info: SegyFormatInfo


