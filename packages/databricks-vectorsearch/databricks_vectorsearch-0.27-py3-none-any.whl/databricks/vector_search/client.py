import logging
import time
import json
from databricks.vector_search.exceptions import InvalidInputException
from databricks.vector_search.utils import OAuthTokenUtils
from databricks.vector_search.utils import RequestUtils
from databricks.vector_search.index import VectorSearchIndex
from mlflow.utils import databricks_utils

class VectorSearchClient:
    """
    A client for interacting with the Vector Search service.

    This client provides methods for managing endpoints and indexes in the Vector Search service.
    """

    def __init__(
        self,
        workspace_url=None,
        personal_access_token=None,
        service_principal_client_id=None,
        service_principal_client_secret=None,
        azure_tenant_id=None,
        azure_login_id=None,
        disable_notice=False,
    ):
        """
        Initialize the VectorSearchClient.

        :param str workspace_url: The URL of the workspace.
        :param str personal_access_token: The personal access token for authentication.
        :param str service_principal_client_id: The client ID of the service principal for authentication.
        :param str service_principal_client_secret: The client secret of the service principal for authentication.
        :param str azure_tenant_id: The tenant ID of Azure for authentication.
        :param str azure_login_id: The login ID of Azure for authentication.
        :param bool disable_notice: Whether to disable the notice message.
        """
        self.workspace_url = workspace_url
        self.personal_access_token = personal_access_token
        self.service_principal_client_id = service_principal_client_id
        self.service_principal_client_secret = service_principal_client_secret
        self.azure_tenant_id = azure_tenant_id
        self.azure_login_id = azure_login_id
        self._is_notebook_pat = False
        if not (
            self.service_principal_client_id and
            self.service_principal_client_secret
        ):
            if self.workspace_url is None:
                host_creds = databricks_utils.get_databricks_host_creds()
                self.workspace_url = host_creds.host
            if self.personal_access_token is None:
                self._is_notebook_pat = True
                host_creds = databricks_utils.get_databricks_host_creds()
                self.personal_access_token = host_creds.token

        self._control_plane_oauth_token = None
        self._control_plane_oauth_token_expiry_ts = None
        self.validate(disable_notice=disable_notice)

    def validate(self, disable_notice=False):
        if not (self.personal_access_token or
                (self.service_principal_client_id and 
                    self.service_principal_client_secret)):
            raise InvalidInputException(
                "Please specify either personal access token or service principal client ID and secret."
            )
        if (self.service_principal_client_id and
                self.service_principal_client_secret and
                not self.workspace_url):
            raise InvalidInputException(
                "Service Principal auth flow requires workspace url"
            )
        if self._is_notebook_pat and not disable_notice:
            print(
                """[NOTICE] Using a notebook authentication token. Recommended for development only. For improved performance, please use Service Principal based authentication. To disable this message, pass disable_notice=True to VectorSearchClient()."""
            )
        elif self.personal_access_token and not disable_notice:
            print(
                """[NOTICE] Using a Personal Authentication Token (PAT). Recommended for development only. For improved performance, please use Service Principal based authentication. To disable this message, pass disable_notice=True to VectorSearchClient()."""
            )


    def _get_token_for_request(self):
        if self.personal_access_token:
            return self.personal_access_token
        if (
            self._control_plane_oauth_token
            and self._control_plane_oauth_token_expiry_ts
            and self._control_plane_oauth_token_expiry_ts - 100 > time.time()
        ):
            return self._control_plane_oauth_token
        if self.service_principal_client_id and \
                self.service_principal_client_secret:
            authorization_details = []
            oauth_token_data = OAuthTokenUtils.get_oauth_token(
                    workspace_url=self.workspace_url,
                    service_principal_client_id=self.service_principal_client_id,
                    service_principal_client_secret=self.service_principal_client_secret,
                    authorization_details=authorization_details,
            ) if not self.azure_tenant_id else OAuthTokenUtils.get_azure_oauth_token(
                    workspace_url=self.workspace_url,
                    service_principal_client_id=self.service_principal_client_id,
                    service_principal_client_secret=self.service_principal_client_secret,
                    authorization_details=authorization_details,
                    azure_tenant_id=self.azure_tenant_id,
                    azure_login_id=self.azure_login_id
            )
            self._control_plane_oauth_token = oauth_token_data["access_token"]
            self._control_plane_oauth_token_expiry_ts = time.time() + oauth_token_data["expires_in"]
            return self._control_plane_oauth_token
        raise Exception("You must specify service principal or PAT token")

    def create_endpoint(self, name, endpoint_type="STANDARD"):
        """
        Create an endpoint.

        :param str name: The name of the endpoint.
        :param str endpoint_type: The type of the endpoint. Must be STANDARD or ENTERPRISE.
        """
        json_data = {"name": name, "endpoint_type": endpoint_type}
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints",
            token=self._get_token_for_request(),
            method="POST",
            json=json_data,
        )

    def get_endpoint(self, name):
        """
        Get an endpoint.

        :param str name: The name of the endpoint.
        """
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{name}",
            token=self._get_token_for_request(),
            method="GET",
        )

    def list_endpoints(self):
        """
        List all endpoints.
        """
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints",
            token=self._get_token_for_request(),
            method="GET",
        )

    def delete_endpoint(self, name):
        """
        Delete an endpoint.

        :param str name: The name of the endpoint.
        """
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{name}",
            token=self._get_token_for_request(),
            method="DELETE",
        )

    def list_indexes(self, name):
        """
        List all indexes for an endpoint.

        :param str name: The name of the endpoint.
        """
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{name}/indexes",
            token=self._get_token_for_request(),
            method="GET",
        )

    def create_delta_sync_index(
            self,
            endpoint_name,
            index_name,
            primary_key,
            source_table_name,
            pipeline_type,
            embedding_dimension=None,
            embedding_vector_column=None,
            embedding_source_column=None,
            embedding_model_endpoint_name=None
    ):
        """
        Create a delta sync index.

        :param str endpoint_name: The name of the endpoint.
        :param str index_name: The name of the index.
        :param str primary_key: The primary key of the index.
        :param str source_table_name: The name of the source table.
        :param str pipeline_type: The type of the pipeline. Must be CONTINUOUS or TRIGGERED.
        :param int embedding_dimension: The dimension of the embedding vector.
        :param str embedding_vector_column: The name of the embedding vector column.
        :param str embedding_source_column: The name of the embedding source column.
        :param str embedding_model_endpoint_name: The name of the embedding model endpoint.
        """
        assert pipeline_type, "Pipeline type cannot be None. Please use CONTINUOUS/TRIGGERED as the pipeline type."
        json_data = {
            "name": index_name,
            "index_type": "DELTA_SYNC",
            "primary_key": primary_key,
            "delta_sync_index_spec": {
                "source_table": source_table_name,
                "pipeline_type": pipeline_type.upper(),
            }
        }
        if embedding_vector_column:
            assert embedding_dimension, "Embedding dimension must be specified if source column is used"
            json_data["delta_sync_index_spec"]["embedding_vector_columns"] = [
                {
                    "name": embedding_vector_column,
                    "embedding_dimension": embedding_dimension
                }
            ]
        elif embedding_source_column:
            assert embedding_model_endpoint_name, \
                "You must specify Embedding Model Endpoint"
            json_data["delta_sync_index_spec"]["embedding_source_columns"] = [
                {
                    "name": embedding_source_column,
                    "embedding_model_endpoint_name": embedding_model_endpoint_name
                }
            ]

        resp = RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{endpoint_name}/indexes",
            token=self._get_token_for_request(),
            method="POST",
            json=json_data,
        )

        index_url = resp.get('status', {}).get('index_url')
        return VectorSearchIndex(
            workspace_url=self.workspace_url,
            index_url=index_url,
            personal_access_token=self.personal_access_token,
            service_principal_client_id=self.service_principal_client_id,
            service_principal_client_secret=self.service_principal_client_secret,
            name=resp["name"],
            endpoint_name=endpoint_name,
            azure_tenant_id=self.azure_tenant_id,
            azure_login_id=self.azure_login_id
        )

    def create_direct_access_index(
            self,
            endpoint_name,
            index_name,
            primary_key,
            embedding_dimension,
            embedding_vector_column,
            schema,
            embedding_model_endpoint_name=None):
        """
        Create a direct access index.

        :param str endpoint_name: The name of the endpoint.
        :param str index_name: The name of the index.
        :param str primary_key: The primary key of the index.
        :param int embedding_dimension: The dimension of the embedding vector.
        :param str embedding_vector_column: The name of the embedding vector column.
        :param dict schema: The schema of the index.
        :param str embedding_model_endpoint_name: The name of the optional embedding model endpoint to use when querying.
        """
        assert schema, """
            Schema must be present when creating a direct access index.
            Example schema: {"id": "integer", "text": "string", \
                "text_vector": "array<float>", "bool_val": "boolean", \
                    "float_val": "float", "date_val": "date"}"
        """
        json_data = {
            "name": index_name,
            "index_type": "DIRECT_ACCESS",
            "primary_key": primary_key,
            "direct_access_index_spec": {
                "embedding_vector_columns": [
                    {
                        "name": embedding_vector_column,
                        "embedding_dimension": embedding_dimension
                    }
                ],
                "schema_json": json.dumps(schema)
            },
        }
        if embedding_model_endpoint_name:
            json_data["direct_access_index_spec"]["embedding_source_columns"] = [
                {
                    "embedding_model_endpoint_name": embedding_model_endpoint_name
                }
            ]
        resp = RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{endpoint_name}/indexes",
            token=self._get_token_for_request(),
            method="POST",
            json=json_data,
        )

        index_url = resp.get('status', {}).get('index_url')
        return VectorSearchIndex(
            workspace_url=self.workspace_url,
            index_url=index_url,
            personal_access_token=self.personal_access_token,
            service_principal_client_id=self.service_principal_client_id,
            service_principal_client_secret=self.service_principal_client_secret,
            name=resp["name"],
            endpoint_name=endpoint_name,
            azure_tenant_id=self.azure_tenant_id,
            azure_login_id=self.azure_login_id
        )

    def get_index(self, endpoint_name, index_name):
        """
        Get an index.

        :param str endpoint_name: The name of the endpoint.
        :param str index_name: The name of the index.
        """
        resp = RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{endpoint_name}/indexes/{index_name}",
            token=self._get_token_for_request(),
            method="GET",
        )
        index_url = resp.get('status', {}).get('index_url')
        return VectorSearchIndex(
            workspace_url=self.workspace_url,
            index_url=index_url,
            personal_access_token=self.personal_access_token,
            service_principal_client_id=self.service_principal_client_id,
            service_principal_client_secret=self.service_principal_client_secret,
            name=index_name,
            endpoint_name=endpoint_name,
            azure_tenant_id=self.azure_tenant_id,
            azure_login_id=self.azure_login_id
        )

    def delete_index(self, endpoint_name, index_name):
        """
        Delete an index.

        :param str endpoint_name: The name of the endpoint.
        :param str index_name: The name of the index.
        """
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{endpoint_name}/indexes/{index_name}",
            token=self._get_token_for_request(),
            method="DELETE",
        )