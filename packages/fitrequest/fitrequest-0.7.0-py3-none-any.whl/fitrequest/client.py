import difflib
import logging
import os
import xml.etree.ElementTree as ET
from http import HTTPStatus
from importlib.metadata import PackageNotFoundError, version
from io import BytesIO
from typing import List, Optional, Union
from urllib.parse import urlparse
from xml.etree.ElementTree import Element

import orjson
from defusedxml.ElementTree import fromstring
from requests import Request, Response, Session
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry

from fitrequest.method_generator import RequestMethod, _MethodsGenerator

try:
    import boto3  # noqa: F401
    import strenum  # noqa: F401

    from fitrequest.utils import AWSSecret, get_secret_from_aws  # noqa: F401

    AWS_CREDENTIALS = True
except ImportError:
    AWS_CREDENTIALS = False

logger = logging.getLogger(__name__)

LIMIT_REQUEST_LINE = (
    4094  # https://docs.gunicorn.org/en/stable/settings.html#limit-request-line
)


class FitRequest(metaclass=_MethodsGenerator):
    _docstring_template: Optional[str] = None
    _methods_binding: Optional[List[dict]] = None
    _retry: Optional[Retry] = None
    _session: Optional[Session] = None
    base_client_name: str
    base_url: Optional[str] = None

    def __init__(
        self, username=None, password=None, response_log_level=None, *args, **kwargs
    ):
        self.base_url = self.base_url or os.environ['CLIENT_BASE_URL']
        self.response_log_level = response_log_level
        if all((AWS_CREDENTIALS, kwargs.get('credentials_from_aws'))):
            default_secret_path = f"/{self.env or ''}/{self.base_client_name.lower()}"
            username = (
                username
                or AWSSecret(
                    **kwargs.get(
                        'username_secret',
                        {'type': 'ssm', 'path': f'{default_secret_path}/username'},
                    )
                ).value
            )
            password = AWSSecret(
                **kwargs.get(
                    'password_secret',
                    {
                        'type': 'secretsmanager',
                        'path': f'{default_secret_path}/password',
                    },
                )
            ).value
        else:
            username = username or os.environ.get(
                f'{self.base_client_name.upper()}_USERNAME', ''
            )
            password = password or os.environ.get(
                f'{self.base_client_name.upper()}_PASSWORD', ''
            )

        self._authenticate(username=username, password=password)
        self._set_kwargs_allowed_for_request()

    def __getattr__(self, name: str):
        closest_match = difflib.get_close_matches(
            name,
            (method for method in dir(self) if callable(getattr(self, method))),
            n=1,
        )
        message = f"'{type(self).__name__}' object has no attribute/method '{name}'."
        if closest_match:
            message += f" Did you mean '{closest_match[0]}'?"
        raise AttributeError(message)

    @property
    def session(self) -> Session:
        if not self._session:
            self._session = Session()
            try:
                package_version = version(self.base_client_name)
            except PackageNotFoundError:
                logger.warning(
                    f'Cannot retrieve package version, either your package is not named {self.base_client_name} '
                    '(as your base_client_name attribute), or it is not installed.'
                )
                package_version = '{version}'
            self._session.headers = {
                'User-Agent': f'fitrequest.{self.base_client_name}.{package_version}'
            }
            if self._retry:
                adapter = HTTPAdapter(max_retries=self._retry)
                self._session.mount('http://', adapter)
                self._session.mount('https://', adapter)
            self._session.auth = self._auth
        return self._session

    def _authenticate(self, username: str, password: str) -> None:
        self._auth = HTTPBasicAuth(username, password)

    def _build_final_url(self, endpoint: str) -> str:
        url = f'{self.base_url}/{endpoint.lstrip("/")}'
        return url if self._is_url_valid(url) else ValueError(f'Invalid URL: {url}')

    def _check_kwargs(self, kwargs: dict) -> dict:
        checked_kwargs = {}
        for key, value in kwargs.items():
            if key not in self._kwargs_allowed_for_request:
                logger.warning(f'Unexpected keyword argument: {key}')
            elif key == 'params':
                checked_kwargs[key] = self._transform_params(value)
            else:
                checked_kwargs[key] = value
        return checked_kwargs

    def _check_request(self, method: RequestMethod, url: str, **kwargs) -> None:
        prepared_request = self.session.prepare_request(
            Request(method=method, url=url, **kwargs)
        )
        if len(prepared_request.url) > LIMIT_REQUEST_LINE:
            raise ValueError(
                f'Request URL is too long: {len(prepared_request.url)} > {LIMIT_REQUEST_LINE}'
            )

    def _handle_http_error(self, response: Response) -> None:
        try:
            response.raise_for_status()
        except HTTPError as e:
            msg = response.text if response.content else ''
            if response.status_code == HTTPStatus.UNAUTHORIZED:
                msg = f'{msg}\nMake sure `{self.base_client_name.upper()}_USERNAME` and `{self.base_client_name.upper()}_PASSWORD` are set as environment variables or provided during initialization.'
            if msg:
                raise HTTPError(msg, response=response) from e
            else:
                raise e

    def _handle_response(
        self, response: Response, raise_for_status: bool = True
    ) -> Union[bytes, BytesIO, Element, List[dict], str]:
        if raise_for_status:
            self._handle_http_error(response)

        content_type = response.headers.get('Content-Type', '').split(';')[0].strip()
        if content_type.endswith('json'):
            return response.json() if response.content else None
        elif content_type.endswith(('json-l', 'jsonlines')):
            return [orjson.loads(line) for line in response.content.splitlines()]
        elif content_type.endswith(('plain', 'html')):
            return response.text
        elif content_type.endswith('xml'):
            return fromstring(response.content)
        elif content_type.endswith('csv'):
            return BytesIO(response.content)
        else:
            return response.content

    @staticmethod
    def _is_url_valid(url: Optional[str]) -> bool:
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except (AttributeError, ValueError):
            return False

    def _request(
        self,
        method: RequestMethod,
        endpoint: str,
        raise_for_status: bool = True,
        resource_id: Optional[str] = None,
        response_key: Optional[str] = None,
        **kwargs,
    ) -> Union[bytes, BytesIO, Element, List[dict], str]:
        url = self._build_final_url(endpoint.format(resource_id))
        logger.info(f'Sending {method.value} request to: {url}')
        kwargs_request = self._check_kwargs(kwargs)
        self._check_request(method=method.value, url=url, **kwargs_request)
        response = self._handle_response(
            self.session.request(
                method=method.value,
                url=url,
                **kwargs_request,
            ),
            raise_for_status=raise_for_status,
        )
        if self.response_log_level:
            logger.log(
                self.response_log_level,
                f'Response from {self.base_client_name}',
                extra={
                    'url': url,
                    'client': self.base_client_name,
                    'response': response,
                },
            )
        return (
            response[response_key]
            if isinstance(response, dict) and response_key
            else response
        )

    def _request_and_save(
        self,
        method: RequestMethod,
        endpoint: str,
        filepath: str,
        raise_for_status: bool = True,
        resource_id: Optional[str] = None,
        response_key: Optional[str] = None,
        **kwargs,
    ) -> None:
        data = self._request(
            method=method,
            endpoint=endpoint,
            raise_for_status=raise_for_status,
            resource_id=resource_id,
            response_key=response_key,
            **kwargs,
        )
        self._save_data(filepath=filepath, data=data)

    def _save_data(
        self,
        filepath: str,
        data: Union[bytes, BytesIO, Element, List[dict], str],
        mode: str = 'xb',
    ):
        logger.info(f'Saving data to file: {filepath}')
        with open(filepath, mode) as file:
            if isinstance(data, bytes):
                file.write(data)
            elif isinstance(data, Element):
                tree = ET.ElementTree(data)
                tree.write(file, encoding='utf-8', xml_declaration=True)
            elif isinstance(data, BytesIO):
                file.write(data.read())
            else:
                file.write(orjson.dumps(data, option=orjson.OPT_INDENT_2))

    def _set_kwargs_allowed_for_request(self) -> None:
        self._kwargs_allowed_for_request = {
            'params',
            'data',
            'headers',
            'cookies',
            'files',
            'auth',
            'timeout',
            'allow_redirects',
            'proxies',
            'hooks',
            'stream',
            'verify',
            'cert',
            'json',
        }

    @staticmethod
    def _transform_params(params: Optional[dict]) -> Optional[dict]:
        if params:
            return {
                k: (','.join([str(x) for x in v]) if isinstance(v, (list, set)) else v)
                for k, v in params.items()
            }
