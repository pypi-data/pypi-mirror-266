import logging
import json
import time
from databricks.vector_search.utils import OAuthTokenUtils
from databricks.vector_search.utils import RequestUtils
from databricks.vector_search.utils import UrlUtils
from mlflow.utils import databricks_utils


class VectorSearchIndex:
    """
    VectorSearchIndex is a helper class that represents a Vector Search Index.

    Those who wish to use this class should not instantiate it directly, but rather use the VectorSearchClient class.
    """
    def __init__(
        self,
        workspace_url,
        index_url,
        name,
        endpoint_name,
        personal_access_token=None,
        service_principal_client_id=None,
        service_principal_client_secret=None,
        azure_tenant_id=None,
        azure_login_id=None,
        # whether or not credentials were explicitly passed in by user in client or inferred by client
        # via mlflow utilities. If passed in by user, continue to use user credentials. If not, can
        # attempt automatic auth refresh for model serving.
        use_user_passed_credentials=False
    ):
        self.workspace_url = workspace_url
        self.index_url = UrlUtils.add_https_if_missing(index_url) \
            if index_url else None
        self.name = name
        self.endpoint_name = endpoint_name
        self.personal_access_token = personal_access_token
        self.service_principal_client_id = service_principal_client_id
        self.service_principal_client_secret = service_principal_client_secret
        if self.personal_access_token and \
                not (self.service_principal_client_id and 
                     self.service_principal_client_secret):
            # In PAT flow, don't use index_url given for DP ingress
            self.index_url = self.workspace_url + f"/api/2.0/vector-search/endpoints/{self.endpoint_name}/indexes/{self.name}"
        self.index_url = self.index_url or (self.workspace_url + f"/api/2.0/vector-search/endpoints/{self.endpoint_name}/indexes/{self.name}") # Fallback to CP
        self.azure_tenant_id = azure_tenant_id
        self.azure_login_id = azure_login_id
        self._control_plane_oauth_token = None
        self._control_plane_oauth_token_expiry_ts = None
        self._read_oauth_token = None
        self._read_oauth_token_expiry_ts = None
        self._write_oauth_token = None
        self._write_oauth_token_expiry_ts = None
        self._use_user_passed_credentials = use_user_passed_credentials

    def _get_token_for_request(self, write=False, control_plane=False):
        try:
            # automatically refresh auth if not passed in by user and in model serving environment
            if not self._use_user_passed_credentials and databricks_utils.is_in_databricks_model_serving_environment():
                return databricks_utils.get_databricks_host_creds().token
        except Exception as e:
            logging.warning(f"Reading credentials from model serving environment failed with: {e} "
                    f"Defaulting to cached vector search token")

        if self.personal_access_token:  # PAT flow
            return self.personal_access_token
        if self.workspace_url in self.index_url:
            control_plane = True
        if (
            control_plane and
            self._control_plane_oauth_token and
            self._control_plane_oauth_token_expiry_ts and
            self._control_plane_oauth_token_expiry_ts - 100 > time.time()
        ):
            return self._control_plane_oauth_token
        if (
            write and
            not control_plane and
            self._write_oauth_token
            and self._write_oauth_token_expiry_ts
            and self._write_oauth_token_expiry_ts - 100 > time.time()
        ):
            return self._write_oauth_token
        if (
            not write and
            not control_plane and
            self._read_oauth_token
            and self._read_oauth_token_expiry_ts
            and self._read_oauth_token_expiry_ts - 100 > time.time()
        ):
            return self._read_oauth_token
        if self.service_principal_client_id and \
                self.service_principal_client_secret:
            authorization_details = json.dumps([{
                "type": "unity_catalog_permission",
                "securable_type": "table",
                "securable_object_name": self.name,
                "operation": "WriteVectorIndex" if write else "ReadVectorIndex"
            }]) if not control_plane else []
            oauth_token_data = OAuthTokenUtils.get_oauth_token(
                workspace_url=self.workspace_url,
                service_principal_client_id=self.service_principal_client_id,
                service_principal_client_secret=self.service_principal_client_secret,
                authorization_details=authorization_details
            ) if not self.azure_tenant_id else OAuthTokenUtils.get_azure_oauth_token(
                workspace_url=self.workspace_url,
                service_principal_client_id=self.service_principal_client_id,
                service_principal_client_secret=self.service_principal_client_secret,
                authorization_details=authorization_details,
                azure_tenant_id=self.azure_tenant_id,
                azure_login_id=self.azure_login_id
            )
            if control_plane:
                self._control_plane_oauth_token = oauth_token_data["access_token"]
                self._control_plane_oauth_token_expiry_ts = time.time() + oauth_token_data["expires_in"]
                return self._control_plane_oauth_token
            if write:
                self._write_oauth_token = oauth_token_data["access_token"]
                self._write_oauth_token_expiry_ts = time.time() + oauth_token_data["expires_in"]
                return self._write_oauth_token
            self._read_oauth_token = oauth_token_data["access_token"]
            self._read_oauth_token_expiry_ts = time.time() + oauth_token_data["expires_in"]
            return self._read_oauth_token
        raise Exception("You must specify service principal or PAT token")

    def upsert(self, inputs):
        """
        Upsert data into the index.

        :param inputs: List of dictionaries to upsert into the index.
        """
        assert type(inputs) == list, "inputs must be of type: List of dictionaries"
        assert all(
            type(i) == dict for i in inputs
        ), "inputs must be of type: List of dicts"
        upsert_payload = {"inputs_json": json.dumps(inputs)}
        return RequestUtils.issue_request(
            url=f"{self.index_url}/upsert-data",
            token=self._get_token_for_request(write=True),
            method="POST",
            json=upsert_payload
        )

    def delete(self, primary_keys):
        """
        Delete data from the index.

        :param primary_keys: List of primary keys to delete from the index.
        """
        assert type(primary_keys) == list, "inputs must be of type: List"
        delete_payload = {"primary_keys": primary_keys}
        return RequestUtils.issue_request(
            url=f"{self.index_url}/delete-data",
            token=self._get_token_for_request(write=True),
            method="DELETE",
            json=delete_payload
        )

    def describe(self):
        """
        Describe the index. This returns metadata about the index.
        """
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{self.endpoint_name}/indexes/{self.name}",
            token=self._get_token_for_request(control_plane=True),
            method="GET",
        )

    def sync(self):
        """
        Sync the index. This is used to sync the index with the source delta table.
        This only works with managed delta sync index with pipeline type="TRIGGERED".
        """
        return RequestUtils.issue_request(
            url=f"{self.workspace_url}/api/2.0/vector-search/endpoints/{self.endpoint_name}/indexes/{self.name}/sync",
            token=self._get_token_for_request(control_plane=True),
            method="POST",
        )

    def similarity_search(
        self,
        columns,
        query_text=None,
        query_vector=None,
        filters=None,
        num_results=5,
        debug_level=1,
        score_threshold=None
    ):
        """
        Perform a similarity search on the index. This returns the top K results that are most similar to the query.

        :param columns: List of column names to return in the results.
        :param query_text: Query text to search for.
        :param query_vector: Query vector to search for.
        :param filters: Filters to apply to the query.
        :param num_results: Number of results to return.
        :param debug_level: Debug level to use for the query.
        :param score_threshold: Score threshold to use for the query.

        """
        json_data = {
            "num_results": num_results,
            "columns": columns,
            "filters_json": json.dumps(filters) if filters else None,
            "debug_level": debug_level
        }
        if query_text:
            json_data["query"] = query_text
            json_data["query_text"] = query_text
        if query_vector:
            json_data["query_vector"] = query_vector
        if score_threshold:
            json_data["score_threshold"] = score_threshold

        return RequestUtils.issue_request(
            url=f"{self.index_url}/query",
            token=self._get_token_for_request(),
            method="GET",
            json=json_data
        )