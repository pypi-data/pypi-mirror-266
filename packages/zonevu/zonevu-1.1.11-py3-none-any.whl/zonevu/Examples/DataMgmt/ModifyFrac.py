import copy
from ...Zonevu import Zonevu
from ...Services.WellService import WellData
from ...DataModels.Completions.FracEntry import FracTypeEnum
from ...Services.CompletionsService import StageUpdateMethodEnum
from ...Services.Error import ZonevuError


# Phase I - Get a frac to copy
def main_modify_frac(zonevu: Zonevu, well_name: str):
    """
    This script will locate a well in ZoneVu, and modify a frac.
    :param zonevu: Zonevu instance
    :param well_name: Name of well to work with
    """
    print('Modifying a frac of a well in ZoneVu')
    well_svc = zonevu.well_service  # Get reference to ZoneVu WebAPI completions service

    # Find the well for which I want to copy a deviation frac
    well = well_svc.get_first_named(well_name)
    if well is None:
        print("Exiting since no well named '%s' found." % well_name)
        exit(1)

    print('Well named "%s" was successfully found' % well_name)
    well_svc.load_well(well, {WellData.fracs})      # Load fracs into well
    wellbore = well.primary_wellbore                # Get reference to wellbore
    # Get reference to the first actual frac job on wellbore
    frac = next((item for item in wellbore.fracs if item.frac_type == FracTypeEnum.Actual), None)
    if frac is None:
        print('Could not locate a suitable frac to modify')
        return

    print("Frac ID = %s:" % frac.id)
    print("   Num Stages = %d:" % len(frac.stages))
    print()
    print("Successful execution.")

    do_modify = True
    frac.description = 'Frac modified from python'  # Change the description
    stage = next((item for item in frac.stages if item.sequence_num == 1), None)    # Get first stage
    stage.note = 'Goodbye'                   # Modify a stage

    if do_modify:
        completions_svc = zonevu.completions_service   # Get reference to ZoneVu WebAPI completions service
        try:
            completions_svc.update_frac(frac, True, StageUpdateMethodEnum.Overwrite)    # Add frac to wellbore in ZoneVu
            print("Modify process was successful")
        except ZonevuError as copy_err:
            print("Could not modify frac because %s" % copy_err.message)
            raise copy_err

        print("Execution was successful")



