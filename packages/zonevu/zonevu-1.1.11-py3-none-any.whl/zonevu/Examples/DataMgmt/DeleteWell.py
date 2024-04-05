from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError


def main(zonevu: Zonevu, well_name: str, delete_code: str) -> None:
    # Deleting wells requires a delete code
    well_svc = zonevu.well_service

    # Find a well by name
    well = well_svc.get_first_named(well_name)
    if well is None:
        print('Could not find a well by that name')
        raise ZonevuError.local('Could not find a well with name "%s"' % well_name)

    well_svc.delete_well(well.id, delete_code)

