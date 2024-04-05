from typing import Optional
from enum import StrEnum
from dataclasses import dataclass
from pathlib import Path
from ...Services.Utils import Naming
from .GriddedData import GriddedData


class GridUsageEnum(StrEnum):
    Undefined = 'Undefined'
    Structural = 'Structural'
    Isopach = 'Isopach'
    Attribute = 'Attribute'


@dataclass
class DataGrid(GriddedData):
    usage: Optional[GridUsageEnum] = GridUsageEnum.Undefined

    def get_v_file_path(self, geomodel_folder: Path) -> Path:
        safe_name = Naming.make_safe_name_default(self.name, 'datagrid', self.id)
        file_path = geomodel_folder / 'datagrids' / ('%s-%s.npy' % (safe_name, self.id))
        return file_path


