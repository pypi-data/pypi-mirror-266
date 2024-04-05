from dataclasses import dataclass
from .GriddedData import GriddedData
from pathlib import Path
from ...Services.Utils import Naming


@dataclass
class Structure(GriddedData):
    formation_id: int = 0
    formation_name: str = ''

    def get_v_file_path(self, geomodel_folder: Path) -> Path:
        safe_name = Naming.make_safe_name_default(self.name, 'structure', self.id)
        file_path = geomodel_folder / 'structures' / ('%s-%s.npy' % (safe_name, self.id))
        return file_path
