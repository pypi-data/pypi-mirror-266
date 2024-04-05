from ..DataModels.Seismic.SeismicSurvey import SeismicSurveyEntry, SeismicSurvey, Volume
from ..DataModels.Seismic.SeismicInfo import SeismicInfo
from .Client import Client, ZonevuError
from typing import Tuple, Union, Dict, Optional, Any, List
from ..Services.Storage import AzureCredential, Storage
from azure.storage.blob import BlobServiceClient
from pathlib import Path


class SeismicService:
    client: Client

    def __init__(self, c: Client):
        self.client = c

    def get_surveys(self, match_token: Optional[str] = None) -> List[SeismicSurveyEntry]:
        """
        Gets a list of seismic surveys whose names start with the provided string token.
        :param match_token: If not provided, all surveys from this zonevu account will be retrieved.
        :return: a list of partially loaded seismic surveys
        """
        url = "seismic/surveys"
        if match_token is not None:
            url += "/%s" % match_token
        items = self.client.get_list(url)
        entries = [SeismicSurveyEntry.from_dict(w) for w in items]
        return entries

    def get_first_named(self, name: str) -> Optional[SeismicSurvey]:
        """
        Get first seismic survey with the specified name, populate it, and return it.
        :param name: name or project to get
        :return: a fully loaded seismic survey
        """
        entries = self.get_surveys(name)
        if len(entries) == 0:
            return None
        surveyEntry = entries[0]
        survey = self.find_survey(surveyEntry.id)
        return survey

    def survey_exists(self, name: str) -> Tuple[bool, int]:
        """
        Determine if a seismic survey with the provided name exists in the users zonevu account.
        :param name:
        :return:
        """
        surveys = self.get_surveys(name)
        exists = len(surveys) > 0
        project_id = surveys[0].id if exists else -1
        return exists, project_id

    def find_survey(self, survey_id: int) -> Optional[SeismicSurvey]:
        """
        Get the seismic survey with the provided system survey id
        :param survey_id:
        :return: a fully loaded seismic survey
        """
        url = "seismic/survey/%s" % survey_id
        item = self.client.get(url)
        project = SeismicSurvey.from_dict(item)
        return project

    def load_survey(self, survey: SeismicSurvey) -> None:
        """
        Fully load the provided partially loaded seismic survey.
        :param survey:
        :return:
        """
        loaded_survey = self.find_survey(survey.id)
        survey.merge_from(loaded_survey)

    def volume_info(self, volume_id: int) -> SeismicInfo:
        """
        Get the Segy, coordinate system, and datum for a specified seismic volume
        :param volume_id:
        :return: an info data structure
        """
        url = "seismic/volumeinfo/%s" % volume_id
        item = self.client.get(url)
        info = SeismicInfo.from_dict(item)
        return info

    def get_download_credential(self, volume: Volume) -> AzureCredential:
        """
        Get a temporary download token for a seismic volume
        :param volume: the specified seismic volume
        :return: A temporary download token
        """
        url = 'seismic/volume/downloadtoken/%s' % volume.id
        item = self.client.get(url, None, False)
        cred = AzureCredential.from_dict(item)
        return cred

    def download_volume(self, volume: Volume, directory: Path, filename: Optional[str] = None) -> None:
        """
        Download a SEGY seismic volume
        :param volume: the specified seismic volume
        :param directory: path for output 3D seismic SEGY file.
        :param filename: optional filename for output volume SEGY file. If not provided, the original SEGY file name is used.
        :return:
        """
        cred = self.get_download_credential(volume)
        blob_svc = BlobServiceClient(account_url=cred.url, credential=cred.token)
        client = blob_svc.get_blob_client(container=cred.container, blob=cred.path)

        exists = client.exists()
        if exists:
            try:
                output_path = directory / filename if filename else directory / volume.segy_filename
                with open(output_path, 'wb') as output_file:
                    total_bytes = 0
                    for chunk in client.download_blob().chunks():
                        total_bytes += len(chunk)
                        output_file.write(chunk)
                        percent_downloaded = round(100 * total_bytes / (1024 * 1024 * volume.size))
                        print('%s%% downloaded' % percent_downloaded)
            except ZonevuError as err:
                print('Download of the requested seismic volume "%s" failed because.' % err.message)
                raise err
        else:
            print('The requested seismic volume "%s" does not exist.' % volume.name)

