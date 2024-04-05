from ...Zonevu import Zonevu
from ...Services.Client import ZonevuError
from ...DataModels.Project import ProjectEntry
from ...Services.ProjectService import ProjectData
from ...Services.Storage import Storage


def main(zonevu: Zonevu, project_name: str, storage: Storage) -> None:
    """
    Find a named project in ZoneVu and in user storage, and compare them
    :param zonevu: Zonevu client instance
    :param project_name: Name of project to retrieve and save
    :param storage: User storage to save projects to
    """
    print('Retrieve the same well from ZoneVu and from Storage and compare')

    # Find well with that name in Zonevu
    project_svc = zonevu.project_service
    project = project_svc.get_first_named(project_name)
    if project is None:
        raise ZonevuError.local('Could not find the project "%s"' % project_name)

    # Load data into well from Zonevu
    project_svc.load_project(project, {ProjectData.all})

    # Get stored well
    stored_project = project.retrieve(project.archive_local_dir_path, storage)
    assert stored_project is not None, 'There was no stored version of that project'

    # Compare
    same_version = project.row_version == stored_project.row_version
    assert same_version, 'Stored version of that project has a different version number that zonevu version'

    same = project == stored_project
    assert same, 'The data in the stored version should match the zonevu version but does not'




