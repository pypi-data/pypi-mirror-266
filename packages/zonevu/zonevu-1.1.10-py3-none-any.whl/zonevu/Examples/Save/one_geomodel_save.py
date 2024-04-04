from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.Storage import Storage
from ...Services.GeomodelService import GeomodelData


def main(zonevu: Zonevu, storage: Storage, geomodel_name: str) -> None:
    """
    Write or update a named geomodel from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save projects to
    :param geomodel_name: Name of well to retrieve and save
    """
    print('Save a project to storage')
    # Find project with that name
    geomodel_svc = zonevu.geomodel_service
    geomodel = geomodel_svc.get_first_named(geomodel_name)
    if geomodel is None:
        raise ZonevuError.local('Could not find the geomodel "%s"' % geomodel_name)

    # Load up first data grid as a test
    # grid = geomodel.data_grids[0]
    # geomodel_svc.download_datagrid_z(grid)

    # Load up first structural surface as a test
    # surface = geomodel.structures[0]
    # geomodel_svc.download_structure_z(surface)

    geomodel_svc.load_geomodel(geomodel, {GeomodelData.all})

    up_to_date = geomodel.current(storage)  # Find out if geomodel is in user storage & if it is current
    if up_to_date:
        print('That geomodel is already saved in user storage and is up to date')
    if not up_to_date:
        geomodel.save(storage)                          # Save geomodel to storage outside ZoneVu
        geomodel.save_documents(zonevu.document_service, storage)







