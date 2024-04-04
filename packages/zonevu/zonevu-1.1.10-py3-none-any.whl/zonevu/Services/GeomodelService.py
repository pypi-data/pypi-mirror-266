from ..DataModels.Geomodels.Geomodel import Geomodel, GeomodelEntry
from ..DataModels.Geomodels.DataGrid import DataGrid, GridUsageEnum
from ..DataModels.Geomodels.Structure import Structure
from ..DataModels.Geospatial.GridGeometry import GridInfo
from ..DataModels.Geomodels.SimpleGrid import SimpleGrid
import numpy as np
from .Client import Client, ZonevuError
from ..Services.CoordinatesService import CoordinatesService
from typing import Optional, List, Set
from strenum import StrEnum


class GeomodelData(StrEnum):
    default = 'default'     # Default behavior is to not load anything extra
    datagrids = 'datagrids'
    structures = 'structures'
    all = 'all'             # If specified, load all data, as long as 'default' flag not present


class GeomodelDataOptions:
    geomodel_data: Set[GeomodelData]

    def __init__(self, geomodel_data: Optional[Set[GeomodelData]]):
        self.geomodel_data = geomodel_data or set()

    def _calc_option(self, project_data: GeomodelData) -> bool:
        return (project_data in self.geomodel_data or self.all) and self.some

    @property
    def all(self):
        return GeomodelData.all in self.geomodel_data

    @property
    def some(self) -> bool:
        return GeomodelData.default not in self.geomodel_data

    @property
    def datagrids(self) -> bool:
        return self._calc_option(GeomodelData.datagrids)

    @property
    def structures(self) -> bool:
        return self._calc_option(GeomodelData.structures)


class GeomodelService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_geomodels(self, match_token: Optional[str] = None) -> List[GeomodelEntry]:
        url = "geomodels"
        if match_token is not None:
            url += "/%s" % match_token
        items = self.client.get_list(url)
        entries = [GeomodelEntry.from_dict(w) for w in items]
        return entries

    def get_first_named(self, name: str) -> Optional[GeomodelEntry]:
        """
        Get first project with the specified name, populate it, and return it.
        :param name: name or project to get
        :return:
        """
        geomodel_entries = self.get_geomodels(name)
        if len(geomodel_entries) == 0:
            return None
        geomodelEntry = geomodel_entries[0]
        geomodel = self.find_geomodel(geomodelEntry.id)
        return geomodel

    def find_geomodel(self, geomodel_id: int) -> Optional[Geomodel]:
        url = "geomodel/%s" % geomodel_id
        item = self.client.get(url)
        geomodel = Geomodel.from_dict(item)
        return geomodel

    def load_geomodel(self, geomodel: Geomodel, geomodel_data: Optional[Set[GeomodelData]]) -> None:
        options = GeomodelDataOptions(geomodel_data)
        loaded_geomodel = self.find_geomodel(geomodel.id)
        geomodel.merge_from(loaded_geomodel)

        if options.datagrids:
            try:
                for datagrid in geomodel.data_grids:
                    self.download_datagrid_z(datagrid)
            except Exception as err:
                print('Could not load geomodel datagrids because %s' % err)

        if options.structures:
            try:
                for structure in geomodel.structures:
                    self.download_structure_z(structure)
            except Exception as err:
                print('Could not load geomodel structures because %s' % err)

    def download_datagrid_z(self, datagrid: DataGrid) -> Optional[np.ndarray]:
        url = "geomodel/%s/zvalues/%s" % ('datagrid', datagrid.id)
        if datagrid.geometry is not None:
            datagrid.z_values = self.__load_z_values(url, datagrid.geometry.grid_info)
            return datagrid.z_values
        else:
            return None

    def upload_datagrid_z(self, datagrid: DataGrid):
        url = "geomodel/datagrid/zvalues/%s" % datagrid.id
        if datagrid.z_values is not None:
            float_values = datagrid.z_values.reshape(-1)
            float_bytes = float_values.tobytes()
            self.client.post_data(url, float_bytes, 'application/octet-stream')

    def download_structure_z(self, structure: Structure) -> Optional[np.ndarray]:
        url = "geomodel/structure/zvalues/%s" % structure.id
        if structure.geometry is not None:
            structure.z_values = self.__load_z_values(url, structure.geometry.grid_info)
            return structure.z_values
        else:
            return None

    def create_geomodel(self, geomodel: Geomodel) -> None:
        raise ZonevuError.local('Not implemented')

    def add_datagrid(self, geomodel: Geomodel, datagrid: DataGrid) -> None:
        url = "geomodel/datagrid/add/%s" % geomodel.id

        datagrid_dict = datagrid.to_dict()
        del datagrid_dict['ZValues']       # Delete ref to the zvalues. We upload those separately

        item = self.client.post(url, datagrid_dict, True, {"overwrite": False})    # Post to server

        server_datagrid = DataGrid.from_dict(item)          # Convert grid as returned from server to Datagrid object
        datagrid.copy_ids_from(server_datagrid)             # Copy server ids of grid created on server to local copy

    def add_simple_grid(self, geomodel: Geomodel, grid: SimpleGrid) -> DataGrid:
        """
        Converts a simple grid to a datagrid, geolocates it, creates it in ZoneVu & uploads the z-values
        @param geomodel:
        @param grid:
        @return: The datagrid that was created on server
        """
        coordinate_service = CoordinatesService(self.client)
        grid_geometry = coordinate_service.simple_to_grid_geometry(grid)
        datagrid = DataGrid()
        datagrid.geometry = grid_geometry
        datagrid.name = grid.name
        datagrid.usage = GridUsageEnum.Structural

        # Fix up z values
        negative_infinity = float('-inf')
        for n in range(len(grid.z_values)):  # Replace any None values with our -inf empty grid value
            if grid.z_values[n] is None:
                grid.z_values[n] = negative_infinity
        z_values = np.array(grid.z_values, dtype=np.float32)
        z_matrix = z_values.reshape(grid.num_rows, grid.num_cols)  # Make 2D array
        datagrid.z_values = z_matrix

        neg_inf = float('-inf')
        mask = z_values != neg_inf
        useful_values = z_values[mask]
        datagrid.average_value = np.average(useful_values).item()   # Make sure these are regular floats.
        datagrid.min_value = np.min(useful_values).item()
        datagrid.max_value = np.max(useful_values).item()

        self.add_datagrid(geomodel, datagrid)
        self.upload_datagrid_z(datagrid)

        return datagrid

    # Internal methods
    def __load_z_values(self, url: str, grid: GridInfo) -> np.ndarray:
        float_bytes = self.client.get_data(url)
        float_array = np.frombuffer(float_bytes, dtype=np.float32)
        z_values = float_array.reshape(grid.inline_range.count, grid.crossline_range.count)
        return z_values
