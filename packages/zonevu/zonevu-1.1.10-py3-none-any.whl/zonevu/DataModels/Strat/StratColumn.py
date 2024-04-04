from typing import Optional, ClassVar
from dataclasses import dataclass, field
from ...DataModels.DataModel import DataModel
from ...DataModels.PrimaryDataObject import PrimaryDataObject, DataObjectTypeEnum
from .Formation import Formation
from pathlib import Path
from ...Services.Storage import Storage


@dataclass
class StratColumn(PrimaryDataObject):
    description: Optional[str] = None
    division: Optional[str] = None
    division_id: Optional[int] = None
    basin: Optional[str] = None
    formations: list[Formation] = field(default_factory=list[Formation])

    archive_dir_name: ClassVar[str] = 'stratcolumns'
    archive_json_filename: ClassVar[str] = 'stratcolumn.json'

    def copy_ids_from(self, source: DataModel):
        super().copy_ids_from(source)
        if isinstance(source, StratColumn):
            DataModel.merge_lists(self.formations, source.formations)

    @property
    def data_object_type(self) -> DataObjectTypeEnum:
        return DataObjectTypeEnum.StratColumn

    @property
    def full_name(self) -> str:
        return self.name

    @property
    def archive_local_dir_path(self) -> Path:
        return Path(self.archive_dir_name) / self.safe_name

    @property
    def archive_local_file_path(self) -> Path:
        return self.archive_local_dir_path / self.archive_json_filename

    def save(self, storage: Storage) -> None:
        # Erase all files in this well folder to avoid inconsistent data
        super().save(storage)

    @classmethod
    def retrieve(cls, dir_path: Path, storage: Storage) -> 'StratColumn':
        project_json_path = dir_path / cls.archive_json_filename
        json_obj = PrimaryDataObject.retrieve_json(project_json_path, storage)
        stratcolumn = cls.from_dict(json_obj)
        return stratcolumn

