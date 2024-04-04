from typing import Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json, LetterCase
from ..DataModel import DataModel
from strenum import StrEnum
from ..Geospatial.GeoBox import GeoBox
import pygeojson as geo
from ...Services.Error import ZonevuError
from pathlib import Path
from ...Services.Utils import Naming
from ...Services.Storage import Storage


class LayerTypeEnum(StrEnum):
    Unspecified = "Unspecified"
    Lease = "Lease"
    Hardline = "Hardline"
    Pad = "Pad"


@dataclass_json(letter_case=LetterCase.PASCAL)
@dataclass
class UserLayer(DataModel):
    """
    A user provided map layer.
    """
    #: Project this map layer is associated with
    project_id: int = -1
    #: Optional description of map layer
    description: Optional[str] = None
    #: Type of map layer
    layer_type: LayerTypeEnum = LayerTypeEnum.Unspecified
    #: Map layer data as a geojson string
    geo_json: Optional[str] = None
    #: Map box that encompasses the map layer
    extents: Optional[GeoBox] = None

    @property
    def geojson(self) -> Optional[geo.FeatureCollection]:
        """
        Courtesy function to convert geojson string into a valid geojson object
        :return:
        """
        fc = geo.loads(self.geo_json or '')
        if fc.bbox is None:
            if self.extents is None:
                return None
            upper_right = self.extents.upper_right
            lower_left = self.extents.lower_left
            minx = min(upper_right.longitude, lower_left.longitude)
            maxx = max(upper_right.longitude, lower_left.longitude)
            miny = min(upper_right.latitude, lower_left.latitude)
            maxy = max(upper_right.latitude, lower_left.latitude)
            bbox = (minx, miny, maxx, maxy)
            features2 = geo.FeatureCollection(fc.features, bbox, fc.type, fc.extra_attributes)  # type: ignore
            return features2
        else:
            if isinstance(fc, geo.FeatureCollection):
                return fc
            raise ZonevuError.local('Unexpected geojson data structure encountered')

    #: Functions to support backup of user layers to local storage
    def get_v_file_path(self, dir_path: Path) -> Path:
        name = self.name if self.name is not None and len(self.name) > 0 else 'Layer'
        blob_path_name = dir_path / 'maplayers' / ('%s.json' % Naming.make_safe_name(name, self.id))
        return blob_path_name

    def save(self, dir_path: Path, storage: Storage) -> None:
        if self.geo_json is None or len(self.geo_json) == 0:
            return
        blob_path_name = self.get_v_file_path(dir_path)
        storage.save_text(blob_path_name, self.geo_json)

    def retrieve(self, project_folder: Path, storage: Storage) -> None:
        blob_path_name = self.get_v_file_path(project_folder)
        if not storage.exists(blob_path_name):
            self.geo_json = None
            return
        self.geo_json = storage.retrieve_text(blob_path_name)

