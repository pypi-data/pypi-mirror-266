from typing import Optional, Union
from dataclasses import dataclass, field
from dataclasses_json import config
from ...DataModels.DataModel import DataModel
from datetime import datetime
from ...DataModels.Helpers import MakeIsodataOptionalField


@dataclass
class Note(DataModel):
    md: float = field(default=0.0, metadata=config(field_name="MD"))
    owner: str = ''
    creation_time: datetime = MakeIsodataOptionalField()
    wellbore_id: int = -1
    description: Optional[str] = None
    category: Optional[str] = None
    category_id: Optional[int] = None
    interpretation: Optional[str] = None
    interpretation_id: Optional[int] = None
