from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import config
from abc import ABC, abstractmethod
from dataclasses import dataclass
from ..DataModel import DataModel
from ..Geospatial.GridGeometry import GridGeometry
import numpy as np
from pathlib import Path
from ...Services.Utils import Naming
from ...Services.Storage import Storage


@dataclass
class GriddedData(DataModel, ABC):
    geometry: Optional[GridGeometry] = None
    description: Optional[str] = None
    average_value: Optional[float] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    z_values: Optional[np.ndarray] = field(default=None, metadata=config(encoder=lambda x: None, decoder=lambda x: []))

    @abstractmethod
    def get_v_file_path(self, geomodel_folder: Path) -> Path:
        pass

    def save(self, dir_path: Path, storage: Storage) -> None:
        if self.z_values is not None:
            file_path = self.get_v_file_path(dir_path)
            storage.save_array(file_path, self.z_values)

    def retrieve(self, well_folder: Path, storage: Storage) -> None:
        file_path = self.get_v_file_path(well_folder)
        self.z_values = storage.retrieve_array(file_path)
