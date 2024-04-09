import base64
import time
import urllib.parse
from typing import List

import requests
from requests import Session, Response
from requests.auth import AuthBase

from .access_token import AccessToken
from .credentials import HttpBasic, HttpBearer, ApiKey, OAuth2, Anonymous, CredentialsInterface
from .exceptions import InvalidAccessTokenException, InvalidCredentialsException
from .token_store import MemoryTokenStore


class AuthenticatorInterface(AuthBase):
    pass


class AnonymousAuthenticator(AuthenticatorInterface):
    def __init__(self, credentials: Anonymous):
        self.credentials = credentials

    def __call__(self, request):
        return request


class HttpBasicAuthenticator(AuthenticatorInterface):
    def __init__(self, credentials: HttpBasic):
        self.credentials = credentials

    def __call__(self, request):
        request.headers["Authorization"] = "Basic " + str(
            base64.b64encode((self.credentials.username + ":" + self.credentials.password).encode('utf-8')))
        return request


class HttpBearerAuthenticator(AuthenticatorInterface):
    def __init__(self, credentials: HttpBearer):
        self.credentials = credentials

    def __call__(self, request):
        request.headers["Authorization"] = "Bearer " + self.credentials.token
        return request


class ApiKeyAuthenticator(AuthenticatorInterface):
    def __init__(self, credentials: ApiKey):
        self.credentials = credentials

    def __call__(self, request):
        request.headers[self.credentials.name] = self.credentials.token
        return request


class OAuth2Authenticator(AuthenticatorInterface):
    EXPIRE_THRESHOLD: int = 60 * 10

    def __init__(self, credentials: OAuth2):
        self.credentials = credentials
        self.scopes = credentials.scopes
        if credentials.token_store:
            self.token_store = credentials.token_store
        else:
            self.token_store = MemoryTokenStore()

    def __call__(self, request):
        request.headers["Authorization"] = "Bearer " + self.get_access_token()
        return request

    def build_redirect_url(self, redirect_url: str, scopes: List[str], state: str) -> str:
        parameters = {
            "response_type": "code",
            "client_id": self.credentials.client_id,
        }

        if redirect_url:
            parameters["redirect_uri"] = redirect_url

        if scopes:
            parameters["scope"] = ",".join(scopes)
        elif self.scopes:
            parameters["scope"] = ",".join(self.scopes)

        if state:
            parameters["state"] = state

        return self.credentials.authorization_url + "?" + urllib.parse.urlencode(parameters)

    def fetch_access_token_by_code(self, code: str) -> AccessToken:
        credentials = HttpBasic(self.credentials.client_id, self.credentials.client_secret)

        headers = {
            "Accept": "application/json",
        }

        data = {
            "grant_type": "authorization_code",
            "code": code,
        }

        response = self.new_http_client(credentials).post(self.credentials.token_url, headers=headers, data=data)

        return self.parse_token_response(response)

    def fetch_access_token_by_client_credentials(self) -> AccessToken:
        credentials = HttpBasic(self.credentials.client_id, self.credentials.client_secret)

        headers = {
            "Accept": "application/json",
        }

        data = {
            "grant_type": "client_credentials",
        }

        if self.scopes:
            data["scope"] = ",".join(self.scopes)

        response = self.new_http_client(credentials).post(self.credentials.token_url, headers=headers, data=data)

        return self.parse_token_response(response)

    def fetch_access_token_by_refresh(self, refresh_token: str) -> AccessToken:
        credentials = HttpBearer(self.get_access_token(False, 0))

        headers = {
            "Accept": "application/json",
        }

        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        }

        response = self.new_http_client(credentials).post(self.credentials.token_url, headers=headers, data=data)

        return self.parse_token_response(response)

    def get_access_token(self, automatic_refresh: bool = True, expire_threshold: int = EXPIRE_THRESHOLD) -> str:
        timestamp = time.time()

        access_token = self.credentials.token_store.get()
        if not access_token or access_token.get_expires_in_timestamp() < timestamp:
            access_token = self.fetch_access_token_by_client_credentials()

        if access_token.get_expires_in_timestamp() > (timestamp + expire_threshold):
            return access_token.access_token

        if automatic_refresh and access_token.refresh_token:
            access_token = self.fetch_access_token_by_refresh(access_token.refresh_token)

        return access_token.access_token

    def parse_token_response(self, response: Response) -> AccessToken:
        if response.status_code != 200:
            raise InvalidAccessTokenException(
                "Could not obtain access token, received a non successful status code: " + str(response.status_code))

        token = AccessToken.from_json(response.content)

        self.token_store.persist(token)

        return token

    def new_http_client(self, credentials: CredentialsInterface) -> Session:
        return HttpClientFactory(AuthenticatorFactory.factory(credentials)).factory()


class AuthenticatorFactory:
    @staticmethod
    def factory(credentials: CredentialsInterface):
        if isinstance(credentials, HttpBasic):
            return HttpBasicAuthenticator(credentials)
        elif isinstance(credentials, HttpBearer):
            return HttpBearerAuthenticator(credentials)
        elif isinstance(credentials, ApiKey):
            return ApiKeyAuthenticator(credentials)
        elif isinstance(credentials, OAuth2):
            return OAuth2Authenticator(credentials)
        elif isinstance(credentials, Anonymous):
            return AnonymousAuthenticator(credentials)
        else:
            raise InvalidCredentialsException("Could not find authenticator for credentials")


class HttpClientFactory:
    def __init__(self, authenticator: AuthenticatorInterface):
        self.authenticator = authenticator

    def factory(self) -> Session:
        session = requests.Session()
        session.auth = self.authenticator
        session.headers['User-Agent'] = 'SDKgen Client v1.0'
        session.headers['Accept'] = 'application/json'
        return session

