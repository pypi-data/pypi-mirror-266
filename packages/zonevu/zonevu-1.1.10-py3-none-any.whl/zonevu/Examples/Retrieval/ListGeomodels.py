from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError


def main_list_geomodels(zonevu: Zonevu):
    geomodel_svc = zonevu.geomodel_service

    print('Geomodels:')
    geomodels = geomodel_svc.get_geomodels()
    for entry in geomodels:
        print('%s (%s)' % (entry.name, entry.id))
        if entry.name != 'Elk Hills':
            continue
        try:
            geomodel = geomodel_svc.find_geomodel(entry.id)
            print('Geomodel %s has %s datagrids and %s structures' %
                  (geomodel.name, len(geomodel.data_grids), len(geomodel.structures)))

        except ZonevuError as err:
            print('Geomodel "%s" had an issue: %s' % (entry.name, err.message))

    print("Execution was successful")

