from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.WellData import WellData
from ...Services.Storage import Storage, FileStorage


def main(zonevu: Zonevu, storage: Storage, well_name: str) -> None:
    """
    Write or update a named well from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save wells to
    :param well_name: Name of well to retrieve and save
    """
    print('Save a well to storage')
    # Find well with that name
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    up_to_date = well.current(storage)  # Find out if well is in user storage & if it is current
    if up_to_date:
        print('That well is already saved in user storage and is up to date')
    if not up_to_date:
        well_svc.load_well(well, {WellData.all})    # Load data into well from ZoneVu
        well.save(storage)                          # Save well to storage outside ZoneVu
        well.save_documents(zonevu.document_service, storage)  # Save well documents to storage outside ZoneVu










