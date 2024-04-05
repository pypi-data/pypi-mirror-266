from typing import Optional
from dataclasses import dataclass, field
from ...DataModels.DataModel import DataModel


@dataclass
class NoteCategory(DataModel):
    description: Optional[str] = None
