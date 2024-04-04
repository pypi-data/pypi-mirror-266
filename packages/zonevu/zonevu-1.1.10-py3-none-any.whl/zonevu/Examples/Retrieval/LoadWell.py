from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...DataModels.Wells.Well import Well
from ...Services.WellData import WellData


def main(zonevu: Zonevu, well_name: str) -> Well:
    print('Retrieve a named well and load all of its well data')
    well_svc = zonevu.well_service
    well = well_svc.get_first_named(well_name)
    if well is None:
        raise ZonevuError.local('Could not find the well "%s"' % well_name)

    # Load up specified well data
    # well_svc.load_well(well, {WellData.logs, WellData.curves})
    well_svc.load_well(well, {WellData.fracs})
    wellbore = well.primary_wellbore
    fracs = wellbore.fracs
    return well




