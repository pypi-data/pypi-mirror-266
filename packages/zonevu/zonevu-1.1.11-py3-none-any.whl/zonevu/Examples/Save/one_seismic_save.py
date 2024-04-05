from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...Services.Storage import Storage
from pathlib import Path


def main(zonevu: Zonevu, storage: Storage, seismic_survey_name: str) -> None:
    """
    Write or update a named survey from a ZoneVu account to user storage.
    :param zonevu: Zonevu client instance
    :param storage: User storage to save surveys to
    :param seismic_survey_name: Name of survey to retrieve and save
    """
    print('Save a survey to storage')
    # Find survey with that name
    seismic_svc = zonevu.seismic_service
    survey = seismic_svc.get_first_named(seismic_survey_name)
    if survey is None:
        raise ZonevuError.local('Could not find the survey "%s"' % seismic_survey_name)

    seismic_svc.load_survey(survey)

    # Test getting download credential
    volume = survey.seismic_volumes[0]
    download_dir = Path('c:/delme/')
    seismic_svc.download_volume(volume, download_dir)

    up_to_date = survey.current(storage)  # Find out if survey is in user storage & if it is current
    if up_to_date:
        print('That survey is already saved in user storage and is up to date')
    if not up_to_date:
        survey.save(storage)                          # Save survey to storage outside ZoneVu
        survey.save_documents(zonevu.document_service, storage)







