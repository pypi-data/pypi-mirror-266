import copy
from ...Zonevu import Zonevu
from ...Services.WellService import WellData
from ...DataModels.Completions.FracEntry import FracTypeEnum
from ...Services.Error import ZonevuError


# Phase I - Get a frac to copy
def main_copy_frac(zonevu: Zonevu, well_name: str, delete_code: str):
    """
    This script will locate a well in ZoneVu, and make a copy of a frac of that well.
    :param zonevu: Zonevu instance
    :param well_name: Name of well to work with
    :param delete_code: delete code to use if an existing copy will be deleted
    """
    print('Making a copy of a frac of a well in ZoneVu')
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
        print('Could not locate a suitable frac to copy')
        return

    print("Frac ID = %s:" % frac.id)
    print("   Num Stages = %d:" % len(frac.stages))
    print()
    print("Successful execution.")

    do_copy = True

    if do_copy:
        # Phase II - Delete Copy if it exists
        completions_svc = zonevu.completions_service   # Get reference to ZoneVu WebAPI completions service
        frac_copy_name = '%s-Copy' % frac.name        # The copied frac will be called this
        print("The copied frac will be named '%s'." % frac_copy_name)
        try:
            # Here we check to see if a frac named "Actual-Copy" already exists, and maybe delete it.
            existing_copy = next((item for item in wellbore.fracs if item.name == frac_copy_name), None)
            if existing_copy is not None:
                print("There was an existing frac named '%s' so deleting it." % frac_copy_name)
                completions_svc.delete_frac(existing_copy, delete_code)
                print("Delete process was successful")
        except ZonevuError as delete_err:
            print("Could not delete frac '%s' because %s" % (frac_copy_name, delete_err.message))
            raise delete_err

        # Phase III - Make a copy of the frac on the wellbore
        try:
            frac_copy = copy.deepcopy(frac)      # Make a local copy of frac including stations.
            frac_copy.name = frac_copy_name             # Name the copy
            completions_svc.add_frac(wellbore, frac_copy)    # Add frac to wellbore in ZoneVu
            print("Copy process was successful")
        except ZonevuError as copy_err:
            print("Could not copy frac because %s" % copy_err.message)
            raise copy_err

        print("Execution was successful")



