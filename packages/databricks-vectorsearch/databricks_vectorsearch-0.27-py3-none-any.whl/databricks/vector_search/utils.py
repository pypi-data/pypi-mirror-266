import requests
import logging
import os
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from functools import lru_cache

class OAuthTokenUtils:

    @staticmethod
    def get_azure_oauth_token(
        workspace_url,
        azure_tenant_id,
        azure_login_id,
        service_principal_client_id,
        service_principal_client_secret,
        authorization_details=None,
    ):
        url = f"https://login.microsoftonline.com/{azure_tenant_id}/oauth2/v2.0/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        resource_identifier = azure_login_id
        assert (azure_login_id and azure_tenant_id), "Both azure_login_id and azure_tenant_id must be specified"
        data = {
            "grant_type": "client_credentials",
            "scope": f"{resource_identifier}/.default",
            "client_id": service_principal_client_id,
            "client_secret": service_principal_client_secret
        }
        azure_response = requests.request(
            url=url,
            headers=headers,
            method="POST",
            data=data
        )
        try:
            azure_response.raise_for_status()
        except Exception as e:
            logging.warn(f"Error retrieving OAuth Token {e}")
            raise Exception(
                f"Response content {azure_response.content}, status_code {azure_response.status_code}"
            )
        aad_token = azure_response.json()['access_token']
        authorization_details = authorization_details or []
        if not authorization_details:
            return azure_response.json()
        url = workspace_url + "/oidc/v1/token"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': '*/*',
        }
        data = {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": aad_token,
            "authorization_details": authorization_details
        }
        response = requests.request(
            url=url,
            headers=headers,
            method="POST",
            data=data
        )
        try:
            response.raise_for_status()
        except Exception as e:
            logging.warn(f"Error retrieving OAuth Token {e}")
            raise Exception(
                f"Response content {response.content}, status_code {response.status_code}"
            )
        return response.json()

    @staticmethod
    def get_oauth_token(
        workspace_url,
        service_principal_client_id,
        service_principal_client_secret,
        authorization_details=None,
    ):
        authorization_details = authorization_details or []
        url = workspace_url + "/oidc/v1/token"
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        data = {
            "grant_type": "client_credentials",
            "scope": "all-apis",
            "authorization_details": authorization_details
        }
        logging.info(f"Issuing request to {url} with data {data} and headers {headers}")
        response = requests.request(
            url=url,
            auth=(service_principal_client_id, service_principal_client_secret),
            headers=headers,
            method="POST",
            data=data
        )
        try:
            response.raise_for_status()
        except Exception as e:
            logging.warn(f"Error retrieving OAuth Token {e}")
            raise Exception(
                f"Response content {response.content}, status_code {response.status_code}"
            )
        return response.json()

@lru_cache(maxsize=64)
def _cached_get_request_session(
        total_retries,
        backoff_factor,
        # To create a new Session object for each process, we use the process id as the cache key.
        # This is to avoid sharing the same Session object across processes, which can lead to issues
        # such as https://stackoverflow.com/q/3724900.
        process_id):
    session = requests.Session()
    retry_strategy = Retry(
        total=total_retries,  # Total number of retries
        backoff_factor=backoff_factor,  # A backoff factor to apply between attempts
        status_forcelist=[429],  # HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session

class RequestUtils:
    session = _cached_get_request_session(
        total_retries=3,
        backoff_factor=1,
        process_id=os.getpid())

    @staticmethod
    def issue_request(url, token, method, params=None, json=None, verify=True):
        headers = dict()
        headers["Authorization"] = f"Bearer {token}"
        response = RequestUtils.session.request(
            url=url,
            headers=headers,
            method=method,
            params=params,
            json=json,
            verify=verify
        )
        try:
            response.raise_for_status()
        except Exception as e:
            logging.warn(f"Error processing request {e}")
            raise Exception(
                f"Response content {response.content}, status_code {response.status_code}"
            )
        return response.json()


class UrlUtils:

    @staticmethod
    def add_https_if_missing(url):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        return url
