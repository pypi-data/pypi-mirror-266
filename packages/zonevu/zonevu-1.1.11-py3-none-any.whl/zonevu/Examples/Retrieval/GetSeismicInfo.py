from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
import json


def main_get_seismicsurvey_info(zonevu: Zonevu, seismic_survey_name: str):
    seismic_svc = zonevu.seismic_service

    print('Getting Seismic Info for seismic survey named "%s"' % seismic_survey_name)
    survey = seismic_svc.get_first_named(seismic_survey_name)
    if survey is None:
        raise ZonevuError.local('Could not locate the seismic survey named %s' % seismic_survey_name)

    # Get info on first volume
    if len(survey.seismic_volumes) == 0:
        print('That seismic survey has no volumes')
        return

    volume = survey.seismic_volumes[0]
    print('Getting seismic info for seismic volume named %s' % volume.name)
    info = seismic_svc.volume_info(volume.id)
    info_dict = info.to_dict()
    print(json.dumps(info_dict, indent=3))

    print("Execution was successful")
