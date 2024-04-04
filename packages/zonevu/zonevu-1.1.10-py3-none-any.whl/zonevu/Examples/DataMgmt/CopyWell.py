import copy
from ...Zonevu import Zonevu
from ...Services.WellService import WellData
from ...Services.Error import ZonevuError


def main_copy_well(zonevu: Zonevu, well_name: str, delete_code: str):
    """
    Retrieve a well and its surveys and make a copy
    :param zonevu: Zonevu instance
    :param well_name: Name of well to work with
    :param delete_code: delete code to use if an existing copy will be deleted
    :return:
    """
    well_svc = zonevu.well_service

    well = well_svc.get_first_named(well_name, True)
    well_svc.load_well(well, {WellData.surveys})  # Load well and its surveys
    print('Well %s%s (id=%d, UWI=%s)' % (well.name, well.number, well.id, well.uwi))
    print()

    # Setup for copy
    well_copy = copy.deepcopy(well)
    well_copy.name = '%s_Copy' % well.name
    well_copy.uwi = '%s 2' % well_copy.name

    # Delete well
    try:
        existing_copy = well_svc.get_first_named(well_copy.full_name)
        if existing_copy is not None:
            well_svc.delete_well(existing_copy.id, delete_code)
    except ZonevuError as error:
        print("Execution failed because %s" % error.message)
        raise error

    # Copy well

    well_svc.create_well(well_copy, {WellData.surveys})     # Copy well and its surveys
    print('Well copy %s%s (id=%d, UWI=%s)' % (well_copy.name, well_copy.number, well_copy.id, well_copy.uwi))
    print()

