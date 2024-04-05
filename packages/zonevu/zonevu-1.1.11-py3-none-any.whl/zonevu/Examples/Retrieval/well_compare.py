from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.WellData import WellData
from ...Services.Storage import Storage


def main(zonevu: Zonevu, well_name: str, storage: Storage) -> None:
    """
    Find a named well in ZoneVu and in user storage, and compare them
    :param zonevu: Zonevu client instance
    :param well_name: Name of well to retrieve and save
    :param storage: User storage to save wells to
    """
    print('Retrieve the same well from ZoneVu and from Storage and compare')

    # Find well with that name in Zonevu
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    # Load data into well from Zonevu
    well_svc.load_well(well, {WellData.all})

    # Get stored well
    stored_well = well.retrieve(well.archive_local_dir_path, storage)
    assert stored_well is not None, 'There was no stored version of that well'

    # Compare
    same_version = well.row_version == stored_well.row_version
    assert same_version, 'Stored version of that well has a different version number that zonevu version'

    same = well == stored_well
    assert same, 'The data in the stored version should match the zonevu version but does not'




