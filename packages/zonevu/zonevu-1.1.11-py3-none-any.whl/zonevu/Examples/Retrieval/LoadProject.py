from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...DataModels.Project import Project
from ...Services.ProjectService import ProjectData


def main(zonevu: Zonevu, project_name: str) -> None:
    print('Retrieve a named project and load all of its well data')
    project_svc = zonevu.project_service
    project = project_svc.get_first_named(project_name)
    if project is None:
        raise ZonevuError.local('Could not find the project "%s"' % project_name)

    # Load up specified project data
    project_svc.load_project(project, {ProjectData.all})
    print('Project load complete')




