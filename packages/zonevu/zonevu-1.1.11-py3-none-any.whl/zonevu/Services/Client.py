import json
import requests
from requests import Response, packages, Session
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from urllib3.exceptions import InsecureRequestWarning
from typing import Union, Dict, Type, Optional, Any, List
from .EndPoint import EndPoint
from strenum import StrEnum
from .Error import ZonevuError


class UnitsSystemEnum(StrEnum):
    Metric = 'Metric'
    US = 'US'


class Client:
    # private
    _headers: Dict[str, str] = {}     # Custom HTTP headers (including Auth header)
    _verify = True      # Whether to check SSL certificate
    _baseurl: str = ''       # ZoneVu instance to call
    _units_system: UnitsSystemEnum    # Units system to use when requesting data
    _session: Session
    host: str

    def __init__(self, endPoint: EndPoint, units: UnitsSystemEnum = UnitsSystemEnum.US):
        self.apikey = endPoint.apikey
        self.host = host = endPoint.base_url
        self._verify = endPoint.verify
        if not self._verify:
            requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning) # type: ignore

        self._baseurl = "https://%s/api/v1.1" % host
        self._headers = {'authorization': 'bearer ' + endPoint.apikey}
        self._units_system = units

        # Setup backoff strategy
        self._session = requests.Session()
        # Define the retry strategy  status_forcelist=[429, 500, 502, 503, 504]
        retry_strategy = Retry(
            total=5,  # Total number of retries status_forcelist=[429, 500, 502, 503, 504]to allow
            status_forcelist=[429],  # List of status codes to retry on
            allowed_methods=["HEAD", "GET", "PUT", "POST", "PATCH", "DELETE", "OPTIONS", "TRACE"],  # List of methods to retry on
            backoff_factor=1  # A factor to multiply the delay between retries
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self._session.mount("https://", adapter)

    def make_url(self, relativeUrl: str, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True):
        if query_params is None:
            query_params = {}
        url = "%s/%s" % (self._baseurl, relativeUrl)
        units = "Meters" if self._units_system == UnitsSystemEnum.Metric else "Feet"
        if include_units:
            query_params['options.distanceunits'] = units
            query_params['options.depthunits'] = units

        for index, (key, value) in enumerate(query_params.items()):
            separator = '?' if index == 0 else '&'
            fragment = "%s%s=%s" % (separator, key, value)
            url += fragment

        return url

    def call_api_get(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> Response:
        if query_params is None:
            query_params = {}
        url = self.make_url(relativeUrl, query_params, include_units)

        # r = requests.get(url, headers=self._headers, verify=self._verify)
        r = self._session.get(url, headers=self._headers, verify=self._verify)
        try:
            textJson = json.loads(r.text)
            textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        except Exception as err:
            pass
        return r

    def get(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> Union[Dict, List, None]:
        r = self.call_api_get(relativeUrl, query_params, include_units)
        Client.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    def get_list(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> List:
        json_obj = self.get(relativeUrl, query_params, include_units)
        if json_obj is None:
            return []
        if not isinstance(json_obj, List):
            raise ZonevuError.local('Did not get expected json list structure from server')
        return json_obj

    def get_dict(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None, include_units: bool = True) -> Dict:
        json_obj = self.get(relativeUrl, query_params, include_units)
        if json_obj is None:
            return {}
        if not isinstance(json_obj, Dict):
            raise ZonevuError.local('Did not get expected json dict structure from server')
        return json_obj

    def get_text(self, relativeUrl: str, encoding: str = 'utf-8', query_params: Optional[Dict[str, Any]] = None) -> str:
        if query_params is None:
            query_params = {}
        url = self.make_url(relativeUrl, query_params)
        r = self._session.get(url, headers=self._headers, verify=self._verify)
        Client.assert_ok(r)
        r.encoding = encoding  # We do this because python assumes strings are utf-8 encoded.
        ascii_text = r.text

        # Test
        r.encoding = 'utf-8'
        utf8_text = r.text

        same = ascii_text == utf8_text

        return ascii_text

    def get_data(self, relativeUrl, query_params: Optional[Dict[str, Any]] = None) -> bytes:
        r = self.call_api_get(relativeUrl, query_params)
        Client.assert_ok(r)
        return r.content

    def call_api_post(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                      query_params: Optional[Dict[str, Any]] = None) -> Response:
        url = self.make_url(relativeUrl, query_params, include_units)
        r = self._session.post(url, headers=self._headers, verify=self._verify, json=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def post(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
             query_params: Optional[Dict[str, Any]] = None) -> Union[Dict, List, None]:
        r = self.call_api_post(relativeUrl, data, include_units, query_params)
        Client.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    def post_return_list(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                         query_params: Optional[Dict[str, Any]] = None) -> List:
        json_obj = self.post(relativeUrl, data, include_units, query_params)
        if json_obj is None:
            return []
        if not isinstance(json_obj, List):
            raise ZonevuError.local('Did not get expected json list structure from server')
        return json_obj

    def post_return_dict(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                         query_params: Optional[Dict[str, Any]] = None) -> Dict:
        json_obj = self.post(relativeUrl, data, include_units, query_params)
        if json_obj is None:
            return {}
        if not isinstance(json_obj, Dict):
            raise ZonevuError.local('Did not get expected json list structure from server')
        return json_obj

    def call_api_post_data(self, relativeUrl: str, data: Union[bytes, str, Dict],
                           content_type: Optional[str] = None) -> Response:
        url = self.make_url(relativeUrl, None)
        the_headers = self._headers.copy()
        if content_type is not None:
            the_headers["content-type"] = content_type
        r = self._session.post(url, headers=the_headers, verify=self._verify, data=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def post_data(self, relativeUrl, data: Union[bytes, str, dict], content_type: Optional[str] = None) -> None:
        r = self.call_api_post_data(relativeUrl, data, content_type)
        Client.assert_ok(r)

    def call_api_delete(self, relativeUrl: str, query_params: Optional[Dict[str, Any]] = None) -> Response:
        url = self.make_url(relativeUrl, query_params)
        r = self._session.delete(url, headers=self._headers, verify=self._verify)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def delete(self, relativeUrl: str, query_params: Optional[Dict[str, Any]] = None) -> None:
        r = self.call_api_delete(relativeUrl, query_params)
        Client.assert_ok(r)

    def call_api_patch(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
                       query_params: Optional[Dict[str, Any]] = None) -> Response:
        url = self.make_url(relativeUrl, query_params, include_units)
        r = self._session.patch(url, headers=self._headers, verify=self._verify, json=data)
        if not r.ok:
            textMsg = ''
            if r.status_code == 404:
                textMsg = r.reason
            else:
                textJson = json.loads(r.text)
                textMsg = textJson['Message'] if ('Message' in textJson) else r.reason
            r.reason = "%s (%s)" % (textMsg, r.status_code)
        return r

    def patch(self, relativeUrl: str, data: Union[dict, list], include_units: bool = True,
              query_params: Optional[Dict[str, Any]] = None) -> Union[Dict, List, None]:
        r = self.call_api_patch(relativeUrl, data, include_units, query_params)
        Client.assert_ok(r)
        json_obj = json.loads(r.text) if r.text else None
        return json_obj

    @staticmethod
    def assert_ok(r: Response):
        if not r.ok:
            # raise ResponseError(r)
            raise ZonevuError.server(r)

