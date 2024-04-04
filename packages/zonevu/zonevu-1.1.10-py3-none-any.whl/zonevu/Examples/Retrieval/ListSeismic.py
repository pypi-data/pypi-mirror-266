from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError


def main_list_seismicsurveys(zonevu: Zonevu):
    seismic_svc = zonevu.seismic_service

    print('Seismic Surveys:')
    seismic_entries = seismic_svc.get_surveys()
    for entry in seismic_entries:
        print('%s (%s)' % (entry.name, entry.id))
        if entry.num_datasets == 0:
            print('  - Seismic Survey has %s datasets' % entry.num_datasets)
        else:
            try:
                survey = seismic_svc.find_survey(entry.id)
                for volume in survey.seismic_volumes:
                    print('   %s - %s (%s) - %s mbytes' % (volume.vintage, volume.name, volume.domain, volume.size))
            except ZonevuError as seismic_err:
                print('  * ERROR - Could not get details on seismic survey "%s"' % entry.name)

    print("Execution was successful")

