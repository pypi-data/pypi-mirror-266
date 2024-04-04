import sys
from .DataModels.Company import Company
from .Services.Error import ZonevuError
from .Services.EndPoint import EndPoint
from .Services.WellService import WellService
from .Services.SurveyService import SurveyService
from .Services.Client import Client, UnitsSystemEnum
from .Services.CompanyService import CompanyService
from .Services.WelllogService import WelllogService
from .Services.GeosteeringService import GeosteeringService
from .Services.ProjectService import ProjectService
from .Services.CoordinatesService import CoordinatesService
from .Services.StratService import StratService
from .Services.GeomodelService import GeomodelService
from .Services.MapService import MapService
from .Services.DocumentService import DocumentService
from .Services.StratService import StratService
from .Services.SeismicService import SeismicService
from .Services.CompletionsService import CompletionsService
from .Services.Utils import Naming
from pathlib import Path


class Zonevu:
    # Represents the ZoneVu version 1.1 API
    # private
    _client: Client
    company: Company

    def __init__(self, endPoint: EndPoint, units_system: UnitsSystemEnum = UnitsSystemEnum.US):
        # Make sure we are running in python 3.11 or later
        correct_python = sys.version_info.major >= 3 and sys.version_info.minor >= 11
        if not correct_python:
            raise ZonevuError.local("Python version is too old. The ZoneVu python library requires python "
                                    "version 3.11 or later.")
        self._client = Client(endPoint, units_system)

    @classmethod
    def init_from_keyfile(cls, units_system: UnitsSystemEnum = UnitsSystemEnum.US) -> 'Zonevu':
        """
        Instantiates an instance of Zonevu from a keyfile whose path is specified as an argument to the script
        See EndPoint.from_keyfile() for details on how to set up a keyfile.
        @return: A reference to the zonevu instance.
        """
        endpoint = EndPoint.from_keyfile()
        zonevu = cls(endpoint, units_system)  # Get zonevu python client
        zonevu.print_notice()       # Check that we can talk to ZoneVu server and print notice.
        return zonevu

    @classmethod
    def init_from_std_keyfile(cls, units_system: UnitsSystemEnum = UnitsSystemEnum.US) -> 'Zonevu':
        """
        Creates an EndPoint instance from a json file named 'zonevuconfig.json, stored in the OS user directory.'
        Here is an example key json file:
        {
            "apikey": "xxxx-xxxxx-xxxxx-xxxx"
        }
        @return: An Endpoint instance
        """
        endpoint = EndPoint.from_std_keyfile()
        zonevu = cls(endpoint, units_system)  # Get zonevu python client
        zonevu.print_notice()  # Check that we can talk to ZoneVu server and print notice.
        return zonevu

    # Services -- use these properties to get an instance of a particular zonevu web api service.
    @property
    def company_service(self) -> CompanyService:
        return CompanyService(self._client)

    @property
    def well_service(self) -> WellService:
        return WellService(self._client)

    @property
    def welllog_service(self) -> WelllogService:
        return WelllogService(self._client)

    @property
    def survey_service(self) -> SurveyService:
        return SurveyService(self._client)

    # @property
    # def curve_service(self) -> CurveService:
    #     return CurveService(self._client)

    @property
    def geosteering_service(self) -> GeosteeringService:
        return GeosteeringService(self._client)

    @property
    def project_service(self) -> ProjectService:
        return ProjectService(self._client)

    @property
    def coordinates_service(self) -> CoordinatesService:
        return CoordinatesService(self._client)

    @property
    def formation_service(self) -> StratService:
        return StratService(self._client)

    @property
    def geomodel_service(self) -> GeomodelService:
        return GeomodelService(self._client)

    @property
    def map_service(self) -> MapService:
        return MapService(self._client)

    @property
    def document_service(self) -> DocumentService:
        return DocumentService(self._client)

    @property
    def strat_service(self) -> StratService:
        return StratService(self._client)

    @property
    def seismic_service(self) -> SeismicService:
        return SeismicService(self._client)

    @property
    def completions_service(self) -> CompletionsService:
        return CompletionsService(self._client)

    # High level API
    # Company
    def get_info(self) -> Company:
        """
        Gets information about the company using this API and the ZoneVu version
        :return: The info
        :rtype: Company info object
        """
        self.company = self.company_service.get_info()
        return self.company

    def print_notice(self) -> None:
        info = self.get_info()
        print()
        print("Zonevu Web API Version %s. Zonevu Server Version %s." % (info.Version, info.RuntimeVersion))
        print(info.Notice)
        print("%s accessing ZoneVu account '%s' at %s" % (info.UserName, info.CompanyName, self._client.host))
        print()

    @property
    def archive_directory(self) -> Path:
        host = self._client.host
        qualifier = 'dev' if host.startswith('dev') else 'local' if host.startswith('local') else ''
        zonevu_name = 'zonevu%s' % qualifier
        root = Naming.create_dir_under_home(zonevu_name) / Naming.make_safe_name(self.company.CompanyName) / 'archive'
        return root

    @property
    def wells_directory(self) -> Path:
        wells_dir = self.archive_directory / 'wells'
        return wells_dir








