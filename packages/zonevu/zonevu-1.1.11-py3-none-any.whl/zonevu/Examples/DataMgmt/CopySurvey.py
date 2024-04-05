import copy
from ...Zonevu import Zonevu
from ...Services.WellService import WellData
from ...Services.Error import ZonevuError
from ...DataModels.Wells.Survey import DeviationSurveyUsageEnum


# Phase I - Get a survey to copy
def main_copy_survey(zonevu: Zonevu, well_name: str, delete_code: str):
    """
    This script will locate a well in ZoneVu, and make a copy of its actual deviation survey.
    :param zonevu: Zonevu instance
    :param well_name: Name of well to work with
    :param delete_code: delete code to use if an existing copy will be deleted
    """
    print('Making a copy of the actual deviation survey of a well in ZoneVu')
    well_svc = zonevu.well_service  # Get reference to ZoneVu WebAPI well service

    # Find the well for which I want to copy a deviation survey
    well = well_svc.get_first_named(well_name)
    if well is None:
        print("Exiting since no well named '%s' found." % well_name)
        exit(1)

    print('Well named "%s" was successfully found' % well_name)
    well_svc.load_well(well, {WellData.surveys})      # Load surveys into well
    wellbore = well.primary_wellbore                # Get reference to wellbore
    # Get reference to the actual deviation survey on wellbore
    survey_actual = next((item for item in wellbore.surveys if item.usage == DeviationSurveyUsageEnum.Actual), None)

    print("Survey ID = %s:" % survey_actual.id)
    print("   Num Stations = %d:" % len(survey_actual.stations))
    print("   Usage: %s" % survey_actual.usage)
    print()
    print("Successful execution.")

    do_copy = True

    if do_copy:
        # Phase II - Delete Copy if it exists
        survey_svc = zonevu.survey_service      # Get reference to ZoneVu WebAPI survey service
        survey_copy_name = "Actual-Copy"        # The copied survey will be called this
        print("The copied survey will be named '%s'." % survey_copy_name)
        try:
            # Here we check to see if a survey named "Actual-Copy" already exists, and maybe delete it.
            existing_copy = next((item for item in wellbore.surveys if item.name == survey_copy_name), None)
            if existing_copy is not None:
                print("There was an existing survey named '%s' so deleting it." % survey_copy_name)
                survey_svc.delete_survey(existing_copy, delete_code)
                print("Delete process was successful")
        except ZonevuError as delete_err:
            print("Could not delete survey '%s' because %s" % (survey_copy_name, delete_err.message))
            raise delete_err

        # Phase III - Make a copy of the survey on the wellbore
        try:
            survey_copy = copy.deepcopy(survey_actual)      # Make a local copy of survey including stations.
            survey_copy.name = survey_copy_name             # Name the copy
            survey_copy.usage = DeviationSurveyUsageEnum.Plan   # Make the copy a plan. ZoneVu support multiple plans.
            survey_svc.add_survey(wellbore, survey_copy)    # Add survey to wellbore in ZoneVu
            print("Copy process was successful")
        except ZonevuError as copy_err:
            print("Could not copy survey because %s" % copy_err.message)

        print("Execution was successful")



