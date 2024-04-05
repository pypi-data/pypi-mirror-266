import copy
from ...Zonevu import Zonevu
from tests.test_globals import get_test_zonevu


def main_list_projects(zonevu: Zonevu):
    project_svc = zonevu.project_service

    print('Projects:')
    project_entries = project_svc.get_projects()
    for entry in project_entries:
        print('%s (%s)' % (entry.name, entry.id))
        project = project_svc.find_project(entry.id)
        if len(project.layers) > 0:
            print('Project %s has %s layers' % (project.name, len(project.layers)))

    print("Execution was successful")

