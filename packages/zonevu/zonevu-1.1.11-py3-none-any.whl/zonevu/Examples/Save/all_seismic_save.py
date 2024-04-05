from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.Storage import Storage
import time


def main_save_seismic(zonevu: Zonevu, storage: Storage):
    """
    Write or update all seismic surveys from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save surveys to
    """
    print('Write all surveys in ZoneVu account to disk - Running...')
    seismic_svc = zonevu.seismic_service          # Reference to Zonevu survey service

    # List surveys in account.  Write them out to storage.
    survey_entries = seismic_svc.get_surveys()     # Get a list of all surveys in zonevu account
    print('Number of surveys retrieved = %s' % len(survey_entries))
    num_updated = 0
    for index, survey_entry in enumerate(survey_entries):
        print('%s, ' % survey_entry.name, end="")
        if index % 8 == 0:
            print()

        survey = survey_entry.seismic_survey  # Convert survey entry into a survey.
        up_to_date = survey.current(storage)  # See if there is a copy of survey in storage & if it is current
        if up_to_date:
            continue        # If the row version of the stored version of the survey the same, no need to save it.

        try:
            # seismic_svc.load_well(survey, {WellData.all})    # Load survey with all well data
            seismic_svc.load_survey(survey)     # Get rest of data for the seismic survey
            survey.save(storage)                # Save survey to storage. Overwrite the survey if it  already exists
            survey.save_documents(zonevu.document_service, storage)   # Save well documents to storage
            num_updated += 1
            time.sleep(.1)       # Give Zonevu a 1-second break.
        except ZonevuError as err:
            print('Could not update survey "%s" because %s' % (survey.full_name, err.message))

    print()
    print('%s surveys were written or updated' % num_updated)
    print('Write all surveys in ZoneVu account to disk - Done.')


