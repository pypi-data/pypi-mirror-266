from __future__ import annotations

import json
from pickle import EMPTY_DICT
# from __future__ import annotations
import requests
import time
from dataclasses import dataclass, asdict, field
from types import MappingProxyType
from typing import Optional

from requests import Response
from urllib.parse import urlparse

from transwarp_hippo_api.conn_mgr import globalConnManager, ConnState, check_hippo_host_port_alive
from transwarp_hippo_api.hippo_type import *


def EMPTY_DICT():
    return {}


'''Define the HippoField data class for storing field information'''


@dataclass
class HippoField:
    name: str  # 字段名
    is_primary_key: bool  # 是否为主键
    data_type: HippoType  # 数据类型
    type_params: dict = field(default_factory=EMPTY_DICT)  # 类型参数，使用EMPTY_DICT作为默认工厂函数


''' Define the HippoConn class for managing and operating Hippo connections '''


class HippoConn:
    def __init__(self, hippo_host_ports: list[str], username: str = 'shiva', pwd: str = 'shiva'):
        self.hippo_host_ports = hippo_host_ports  # Initialize the host and port for the connection
        for hp in self.hippo_host_ports:  # Check the status of each host and port, if the connection is normal, add it to the global connection manager
            if check_hippo_host_port_alive(hp):
                globalConnManager.add_conn(hp, ConnState.ACTIVE)
            else:
                globalConnManager.add_conn(hp, ConnState.FAILED)

        self.username = username
        self.pwd = pwd

    # # Define the default JSON request header, only including the content type 'application/json'
    default_json_header = MappingProxyType({
        'Content-Type': 'application/json',
    })

    # Define a method for generating the URL of Hippo
    def make_hippo_url(self, conn_host_port: str):
        return conn_host_port + "/hippo/v1"

    # Define a method for put requests, used for sending put requests to the Hippo server
    def put(self, component_url, js_data: str, headers=default_json_header):
        url_base = "http://" + str(globalConnManager.get_available_conn_from_view(self.hippo_host_ports))
        url = self.make_hippo_url(url_base) + component_url
        return requests.put(url, auth=(self.username, self.pwd), headers=headers, json=js_data)

    # Define a method for delete requests, used for sending delete requests to the Hippo server
    def delete(self, component_url, js_data: str, headers=default_json_header):
        url_base = "http://" + globalConnManager.get_available_conn_from_view(self.hippo_host_ports)
        url = self.make_hippo_url(url_base) + component_url
        return requests.delete(url, auth=(self.username, self.pwd), headers=headers, json=js_data)

    # # Define a method for get requests, used for sending get requests to the Hippo server, simple retry logic is implemented here
    def get(self, component_url, js_data: str, headers=default_json_header, retry_max: int = 3):
        retry_max_count = retry_max
        while retry_max_count > 0:
            this_available_host_port = None
            try:
                this_available_host_port = globalConnManager.get_available_conn_from_view(self.hippo_host_ports)
                url_base = "http://" + this_available_host_port
                url = self.make_hippo_url(url_base) + component_url
                return requests.get(url, auth=(self.username, self.pwd), headers=headers, json=js_data)
            except requests.exceptions.ConnectionError as ce:
                # 对于get请求，做一个简单的重试
                if this_available_host_port is not None:
                    globalConnManager.mark_conn_state(this_available_host_port, ConnState.FAILED)
                retry_max_count -= 1
                if retry_max_count == 0:
                    raise ce

    # Define a method for post requests, used for sending post requests to the Hippo server
    def post(self, component_url, js_data: str, headers=default_json_header):
        url_base = "http://" + globalConnManager.get_available_conn_from_view(self.hippo_host_ports)
        url = self.make_hippo_url(url_base) + component_url
        return requests.post(url, auth=(self.username, self.pwd), headers=headers, json=js_data)

    # Define a static method for handling JSON responses, if the response status code is 200, return the JSON data, otherwise throw an exception
    @staticmethod
    def handle_json_resp(resp: Response) -> dict:
        if resp.status_code == 200:
            s = resp.content
            return json.loads(s)
        else:
            js = resp.json()
            r = "Error message from hippo server:" + js["error"]["reason"]
            raise ValueError(r)


''' Define the HippoTableMeta data class for storing table metadata information '''


@dataclass
class HippoTableMeta:
    tbl_name: str
    auto_id: bool
    schema: list[HippoField]
    n_replicas: int
    n_shards: int
    db_name: str


''' Define the HippoTable class for managing and operating Hippo tables '''


class HippoTable:
    def __init__(self, hippo_conn: HippoConn, tbl_meta: HippoTableMeta):
        self.hippo_conn = hippo_conn
        self.tbl_meta = tbl_meta
        self.tbl_name = tbl_meta.tbl_name
        self.schema = tbl_meta.schema

    # Define the __str__ method, used to display the table name and field information when printing the HippoTable object
    def __str__(self):
        if self.schema is None:
            return f"HippoTable({self.tbl_name}, fields: N/A)"
        else:
            return f"HippoTable({self.tbl_name}, fields: [{','.join([f'{f.name}:{f.data_type.value}' for f in self.schema])}])"

    # Define an internal method for handling data operations on the table, including insertion, updating, deletion, etc.
    def _manipulate_rows(self, cols_like, op_type: str = "insert"):

        """
                Used to handle data operations on the table, including insertion, updating, deletion, etc.

                Parameters:
                    cols_like: A list of column data, each element is a list representing all data of one column.
                    op_type: The operation type, which can be "insert", "update", "upsert", or "delete".

                Returns:
                    If the operation is successful, return True. Otherwise, a ValueError exception is thrown.
    """

        if self.tbl_meta.auto_id and op_type == "insert" and len(cols_like) != len(self.schema):
            schema = self.schema[1:]
        else:
            schema = self.schema

        assert len(cols_like) == len(
            schema), f"to insert data columns({len(cols_like)}) does not match cols in schema({len(schema)})"

        fields_data = []

        rows_num = -1
        for idx, col in enumerate(cols_like):
            col_name = schema[idx].name

            data = cols_like[idx]
            if not isinstance(data, list):
                raise TypeError(f"to insert data column {idx} is not a list")
            col_len = len(data)
            if rows_num != -1 and rows_num != col_len:
                raise ValueError(f"to insert data column rows {col_len} does not match previous row number {rows_num}")
            rows_num = col_len

            this_field_data = {
                "field_name": col_name,
                "field": data,
            }
            fields_data.append(this_field_data)

        req_data = {
            "fields_data": fields_data,
            "num_rows": rows_num,
            "op_type": op_type
        }

        js = json.dumps(req_data)
        js = json.loads(js)
        resp = self.hippo_conn.put(f"/{self.tbl_name}/_bulk?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        if resp.status_code == 200:
            info = json.loads(resp.text)
            failures = info.get("failures")
            if failures is not None:
                raise ValueError(f"{info}")
            else:
                return True
        else:
            error_dict = json.loads(resp.content)
            reason = error_dict["error"]["reason"]
            type = error_dict["error"]["type"]
            raise ValueError(f"error type:{str(type)},reason:{str(reason)}")

    # Define the method for inserting rows, which internally calls the _manipulate_rows method.
    def insert_rows(self, cols_like):

        """
                Insert row data.

                Parameters:
                    cols_like: A list of column data, each element is a list representing all data of one column.

                Returns:
                    If the insertion is successful, return True. Otherwise, a ValueError exception is thrown.
        """
        return self._manipulate_rows(cols_like, "insert")

    # Define the method for updating rows, which internally calls the _manipulate_rows method.
    def update_rows(self, cols_like):

        """
                Update row data.

                Parameters:
                    cols_like: A list of column data, each element is a list representing all data of one column.

                Returns:
                    If the update is successful, return True. Otherwise, a ValueError exception is thrown.
        """
        return self._manipulate_rows(cols_like, "update")

    # Define the method for inserting or updating rows, which internally calls the _manipulate_rows method.
    def upsert_rows(self, cols_like):

        """
                Insert or update row data.

                Parameters:
                    cols_like: A list of column data, each element is a list representing all data of one column.

                Returns:
                    If the operation is successful, return True. Otherwise, a ValueError exception is thrown.
        """
        return self._manipulate_rows(cols_like, "upsert")

    # Define the method for deleting rows, which internally calls the _manipulate_rows method.
    def delete_rows(self, cols_like):

        """
                Delete row data.

                Parameters:
                    cols_like: A list of column data, each element is a list representing all data of one column.

                Returns:
                    If the deletion is successful, return True. Otherwise, a ValueError exception is thrown.
        """
        return self._manipulate_rows(cols_like, "delete")

    # Bulk delete data. The expr argument specifies the condition for the rows to be deleted. For example, "age > 18".
    def delete_rows_by_query(self, expr: str = "",
                             wait_for_completion=True, timeout: str = "2m"):

        """
                Bulk delete data. The expr argument specifies the condition for the rows to be deleted. For example, "age > 18".

                Args:
                    expr: The condition expression for deletion.
                    wait_for_completion: Whether to wait for completion of the deletion, default is True.
                    timeout: Timeout duration, default is "2m".

                Returns:
                    If the deletion is successful, returns the job status. Otherwise, a ValueError exception is raised.
        """

        data = {
            "database_name": self.tbl_meta.db_name,
            "table_name": self.tbl_name,
            "expr": expr,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout
        }
        js = json.dumps(data)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(f"/_delete_by_query?pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"bcannot delete rows due to return error:{error_info}")
        else:
            resp = self.hippo_conn.post(f"/_delete_by_query?pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"cannot delete rows due to return error:{error_info}")

    # Create an index. This method is used to create an index on the specified field to speed up the query.
    def create_index(self, field_name: str, index_name: str, index_type: IndexType, metric_type: MetricType, **kwargs):

        """
                Create an index on the specified field.

                Args:
                    field_name: The name of the field to create the index on.
                    index_name: The name of the newly created index.
                    index_type: The type of index, should be a value of the IndexType enum.
                    metric_type: The type of metric, should be a value of the MetricType enum.
                    **kwargs: Other optional arguments, used to specify additional settings when creating the index.

                Returns:
                    If creation is successful, returns True. Otherwise, a ValueError exception is raised.
        """

        req = {
            "field_name": field_name,
            "index_name": index_name,
            "metric_type": metric_type.value,
            "index_type": index_type.value,
            "params": kwargs
        }

        js = json.dumps(req)
        js = json.loads(js)

        resp = self.hippo_conn.put(
            f"/{self.tbl_name}/_create_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r["acknowledged"]:
            return True
        else:
            raise ValueError("cannot create index due to return error.")

    #  Create a scalar index. Used to create a scalar index on the specified fields.
    def create_scalar_index(self, field_names: list[str], index_name: str):

        """
                Create a scalar index on the specified fields.

                Args:
                    field_names: The list of field names to create the index on.
                    index_name: The name of the newly created scalar index.

                Returns:
                    If creation is successful, returns True. Otherwise, a ValueError exception is raised.
        """

        data = {
            "index_name": index_name,
            "field_names": field_names
        }

        js = json.dumps(data)
        js = json.loads(js)

        resp = self.hippo_conn.put(
            f"/{self.tbl_name}/_create_scalar_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r["acknowledged"]:
            return True
        else:
            raise ValueError("cannot create index due to return error.")

    # Delete a scalar index. Delete the corresponding scalar index by the index name.
    def delete_scalar_index(self, index_name: str):

        """
                Delete the corresponding scalar index by the index name.

                Args:
                    index_name: The name of the index to be deleted.

                Returns:
                    If deletion is successful, returns True. Otherwise, a ValueError exception is raised.
        """

        data = {
            "index_name": index_name
        }

        js = json.dumps(data)
        js = json.loads(js)

        resp = self.hippo_conn.delete(
            f"/{self.tbl_name}/_drop_scalar_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r["acknowledged"]:
            return True
        else:
            raise ValueError("cannot create index due to return error.")

    # Delete an index. Delete the corresponding index by the index name.
    def drop_index(self, index_name: str):

        """
                Delete the corresponding index by the index name.

                Args:
                    index_name: The name of the index to be deleted.

                Returns:
                    If deletion is successful, returns True. Otherwise, a ValueError exception is raised.
        """

        assert isinstance(index_name, str)
        return self.drop_indexes([index_name])

    # Delete multiple indexes. Multiple indexes can be deleted at the same time.
    def drop_indexes(self, index_names: list[str]):

        """
                Multiple indexes can be deleted at the same time.

                Args:
                    index_names: The list of index names to be deleted.

                Returns:
                    If deletion is successful, returns True. Otherwise, a ValueError exception is raised.
        """

        assert all(',' not in ind_name for ind_name in index_names), "index name should not contains ','"
        req = {
            "index_name": ','.join(index_names),
        }

        js = json.dumps(req)
        js = json.loads(js)

        resp = self.hippo_conn.delete(
            f"/{self.tbl_name}/_drop_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r["acknowledged"]:
            return True
        else:
            raise ValueError("cannot drop index due to return error.")

    # Activate an index. Activate the corresponding index by the index name.
    def activate_index(self, index_name: str, wait_for_completion: bool = True, timeout: str = "2m"):
        """
                Activate the corresponding index by the index name.

                Args:
                    index_name: The name of the index to be activated.
                    wait_for_completion: Whether to wait for activation to complete, default is True.
                    timeout: Timeout duration, default is "2m".

                Returns:
                    If activation is successful, returns True. Otherwise, a ValueError exception is raised.
        """

        req = {
            "index_name": index_name,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_activate_embedding_index?database_name={self.tbl_meta.db_name}&pretty",
                js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"activate index return status: {st}, error info: {error_info}")
        else:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_activate_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"activate index return status: {st}, error info: {error_info}")

    # Build an index. Build the specified index.
    def build_index(self, index_name: str, wait_for_completion: bool = True, timeout: str = "2m"):

        """
                Build the specified index.

                Args:
                    index_name: The name of the index to be built.
                    timeout: Timeout duration, default is "2m".

                Returns:
                    If the build is successful, returns True. Otherwise, an Exception exception is raised.
        """

        req = {
            "index_name": index_name,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_rebuild_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"build index return status: {st}, error info: {error_info}")

        else:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_rebuild_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"build index return status: {st}, error info: {error_info}")

    # Release an index. Release the corresponding index by the index name.
    def release_index(self, index_name: str, wait_for_completion: bool = True, timeout: str = "2m"):

        """
                Release the specified index.

                Args:
                    index_name: The name of the index to be released.
                    wait_for_completion: Whether to wait for release to complete, default is True.
                    timeout: Timeout duration, in minutes, default is "2m".

                Returns:
                    If release is successful, returns the job status. Otherwise, a ValueError exception is raised.
        """

        req = {
            "index_name": index_name,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_release_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"release index return status: {st}, error info: {error_info}")

        else:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_release_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"release index return status: {st}, error info: {error_info}")

    # Load an index. Load the specified index for querying
    def load_index(self, index_name: str, wait_for_completion: bool = True, timeout: str = "2m"):

        """
                Load the specified index.

                Args:
                    index_name: The name of the index to be loaded.
                    timeout: Timeout duration, default is "2m".

                Returns:
                    If the load is successful, returns True. Otherwise, an Exception exception is raised.
        """
        req = {
            "index_name": index_name,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_load_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"load index return status: {st}, error info: {error_info}")

        else:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_load_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"load index return status: {st}, error info: {error_info}")

    # Enable/Disable auto compaction of the vector index.
    def index_auto_compaction(self, index_name: str, enable_auto_compaction: bool = True,
                              wait_for_completion: bool = True, timeout: str = "2m"):
        """
                Enable/Disable the auto compaction of the vector index.

                Args:
                    index_name: The name of the index to be activated.
                    enable_auto_compaction: Whether to enable auto compaction.
                    wait_for_completion: Whether to wait for activation to complete, default is True.
                    timeout: Timeout duration, in seconds, default is 120 seconds.

                Returns:
                    If the modification is successful, returns True. Otherwise, a ValueError exception is raised.
            """

        req = {
            "index_name": index_name,
            "enable_auto_compaction": enable_auto_compaction,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_embedding_index_auto_compaction?database_name={self.tbl_meta.db_name}&pretty",
                js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"index_auto_compaction return status: {st}, error info: {error_info}")

        else:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_embedding_index_auto_compaction?database_name={self.tbl_meta.db_name}&pretty",
                js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"index_auto_compaction return status: {st}, error info: {error_info}")

    # Manually compact the vector index.
    def compact_index(self, index_name: str, wait_for_completion: bool = True, timeout: str = "2m"):
        """
                    Manually compact the vector index.

                Args:
                    index_name: The name of the index to be compacted.
                    wait_for_completion: Whether to wait for compaction to complete, default is True.
                    timeout: Timeout duration, in seconds, default is 120 seconds.

                Returns:
                    If compaction is successful, returns True. Otherwise, a ValueError exception is raised.
        """

        req = {
            "index_name": index_name,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_compact_embedding_index?database_name={self.tbl_meta.db_name}&pretty",
                js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"compact_index return status: {st}, error info: {error_info}")
        else:
            resp = self.hippo_conn.post(
                f"/{self.tbl_name}/_compact_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"compact_index return status: {st}, error info: {error_info}")

    # Retrieve indexes. Retrieve all indexes in the current table.
    def get_index(self):

        """
                Retrieve all indexes in the current table.

                Returns:
                    Returns a dictionary containing all indexes.
        """

        resp = self.hippo_conn.get(
            f"/{self.tbl_name}/_get_embedding_index?database_name={self.tbl_meta.db_name}&pretty", js_data=None)
        r = HippoConn.handle_json_resp(resp)
        return r

    # Get settings. Get the setting information for the current table.
    def get_settings(self) -> dict:

        """
                Get the setting information for the current table.

                Returns:
                    Returns a dictionary containing all settings.
        """
        resp = self.hippo_conn.get(f"/{self.tbl_name}/_settings?database_name={self.tbl_meta.db_name}&pretty",
                                   js_data=None)
        r = HippoConn.handle_json_resp(resp)
        return r

    # Update settings. Update the setting information for the current table.
    def update_settings(self, **kwargs):
        """
                Update the setting information for the current table.

                Args:
                    **kwargs: A dictionary containing the settings to be updated.

                Returns:
                    If the update is successful, returns True. Otherwise, returns False.
        """

        req = kwargs
        js = json.dumps(req)
        js = json.loads(js)

        resp = self.hippo_conn.put(f"/{self.tbl_name}/_settings?database_name={self.tbl_meta.db_name}&pretty",
                                   js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if 'acknowledged' in r and r['acknowledged'] == True:
            return True
        else:
            return False

    def count(self, expr=None) -> int:

        """
        Get the number of rows for the current table.

        Args:
            expr (str): Optional parameter to specify an additional expression.

        Returns:
            int: The number of rows.
        """
        if expr is None:
            resp = self.hippo_conn.get(f"/{self.tbl_name}/_count?database_name={self.tbl_meta.db_name}&pretty",
                                       js_data=None)
        else:
            req = {
                "expr": expr
            }
            js = json.dumps(req)
            js = json.loads(js)
            resp = self.hippo_conn.get(f"/{self.tbl_name}/_count?database_name={self.tbl_meta.db_name}&pretty",
                                       js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200:
            return r.get('total')
        else:
            return resp.content

    # Query scalar. Query the table according to the specified output fields and expression.
    def query_scalar(self,
                     output_fields: list[str],
                     expr: str,
                     limit: int,
                     only_explain:bool = False
                     ):

        """
                Query the table according to the specified output fields and expression.

                Args:
                    output_fields: The list of output fields.
                    expr: The query expression.
                    limit：output count
                    only_explain：Whether to only execute explain defalut false
                Returns:
                    Returns a dictionary containing the query result.
        """

        req = {
            "output_fields": output_fields,
            "expr": expr,
            "limit": limit,
            "only_explain": only_explain
        }
        js = json.dumps(req)
        js = json.loads(js)

        resp = self.hippo_conn.get(f"/{self.tbl_name}/_query?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        result = HippoConn.handle_json_resp(resp)

        if only_explain:
            return result

        this_query_result = result.get("fields_data")

        this_query_ret_result = {}

        for col_data in this_query_result:
            field_name = col_data.get("field_name")
            field_values = col_data.get("field_values", [])
            this_query_ret_result[field_name] = field_values

        return this_query_ret_result

    # Query. Query the table according to the specified query parameters and return the result.
    def query(self,
              search_field: str,
              vectors,
              output_fields: list[str],
              topk: int,
              metric_type: str = 'l2',
              dsl: str = None,
              round_decimal: int = None,
              only_explain=None,
              with_profile=None,
              **params,
              ) -> list[HippoResult]:
        """
                        Query the table according to the specified query parameters and return the result.

                        Args:
                            search_field: The name of the search field.
                            vectors: The list of vectors for search.
                            output_fields: The list of output fields.
                            topk: The maximum number of results to return.
                            metric_type: The type of metric, default is 'l2'.
                            dsl: The specified Domain Specific Language (optional).
                            round_decimal: decimal places to retain after scores defalut 2
                            only_explain: Whether to only execute explain defalut false
                            **params: Other query parameters.

                        Returns:
                            Returns a list containing the query result.
                """

        flag = ""
        for schema in self.schema:
            if (schema.name == search_field):
                flag = schema.data_type.value

        point = False
        if round_decimal is not None or only_explain is not None or with_profile is not None:
            point = True
            if round_decimal is None:
                round_decimal = 2
            if only_explain is None:
                only_explain = False
            if with_profile is None:
                with_profile = False
        else:
            round_decimal = 2
            only_explain = False
            with_profile = False

        if flag == HippoType.BINARY_VECTOR.value:
            req = {
                "output_fields": output_fields,
                "search_params": {
                    "anns_field": search_field,
                    "topk": topk,
                    "params": params,
                },
                "binary_vectors": vectors,
                "round_decimal": round_decimal,
                "only_explain": only_explain,
                "with_profile": with_profile
            }
        elif flag == HippoType.SPARSE_FLOAT_VECTOR.value:
            req = {
                "output_fields": output_fields,
                "search_params": {
                    "anns_field": search_field,
                    "topk": topk,
                    "params": params
                },
                "sparse_vectors": vectors,
                "round_decimal": round_decimal,
                "only_explain": only_explain,
                "with_profile": with_profile
            }
        elif flag == HippoType.FLOAT_VECTOR.value:
            if point:
                req = {
                    "output_fields": output_fields,
                    "search_params": {
                        "anns_field": search_field,
                        "topk": topk,
                        "params": params,
                    },
                    "vectors": vectors
                }
            else:
                req = {
                    "output_fields": output_fields,
                    "search_params": {
                        "anns_field": search_field,
                        "topk": topk,
                        "params": params,
                    },
                    "vectors": vectors,
                    "round_decimal": round_decimal,
                    "only_explain": only_explain,
                    "with_profile": with_profile
                }
        else:
            req = {
                "output_fields": output_fields,
                "search_params": {
                    "anns_field": search_field,
                    "topk": topk,
                    "params": params,
                    "metric_type": metric_type,
                },
                "vectors": vectors,
            }

        if dsl is not None:
            req["dsl"] = dsl

        js = json.dumps(req)
        js = json.loads(js)
        resp = self.hippo_conn.get(f"/{self.tbl_name}/_search?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        result = HippoConn.handle_json_resp(resp)

        try:
            if result.get("num_queries") != len(vectors):
                raise RuntimeError(
                    f"internal error, return query number({result.get('num_queries')}) not equal to input query number({len(vectors)}).")

            total_result = []
            if only_explain:
                total_result.append(result)
                return total_result

            query_results = result.get("results")
            assert query_results is not None, "internal error, result should not be None."

            for qr in query_results:
                total_result.append(None)

            for qr in query_results:
                query_id = qr.get("query")
                this_query_result = qr.get("fields_data")

                this_query_ret_result = {}

                for col_data in this_query_result:
                    field_name = col_data.get("field_name")
                    field_values = col_data.get("field_values", [])
                    scores = qr.get("scores")

                    # 当前结果不够的时候，无法保障topk条，我们先不检查了 TODO
                    # assert dsl is not None or len(field_values) == topk, f"return values number({len(field_values)}) mismatch with topk({topk})"
                    # assert dsl is not None or len(scores) == topk, f"return scores number({len(field_values)}) mismatch with topk({topk})"

                    this_query_ret_result[field_name] = field_values
                    this_query_ret_result[field_name + "%scores"] = scores

                total_result[query_id] = this_query_ret_result
        except BaseException as e:
            raise ValueError(f"error during process result, exception -> is {e}. \nreturn json is {resp.json()}")
        return total_result

    def add_columns(self, fields: list[HippoField]):
        """
                Add new columns to the current table.

                Args:
                    fields (list[HippoField]): A list of HippoField objects representing the columns to be added.

                Returns:
                    bool: True if the addition is successful.

                Raises:
                    ValueError: If the addition process is not acknowledged, a ValueError exception is raised.
        """
        fields_for_req = [asdict(f) for f in fields]
        data = {
            "fields": fields_for_req
        }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.post(f"/{self.tbl_name}/_add_columns?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)  
    
    def delete_columns(self, column_names:list):
        """
                Delete specified columns from the current table.

                Args:
                    column_names (list): A list of column names to be deleted.

                Returns:
                    bool: True if the deletion is successful.

                Raises:
                    ValueError: If the deletion process is not acknowledged, a ValueError exception is raised.
        """
        data = {
            "fields": column_names
        }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.post(f"/{self.tbl_name}/_drop_columns?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)

    def rename_columns(self, fields_renaming:list[dict]):
        """
                Rename specified columns in the current table.

                Args:
                    fields_renaming (list): A list of dictionaries where each dictionary represents the renaming of a column.
                                        Each dictionary should have the format {"old_column_name": "new_column_name"}.

                Returns:
                    bool: True if the renaming is successful.

                Raises:
                    ValueError: If the renaming process is not acknowledged, a ValueError exception is raised.
        """

        data = {
            "fields_renaming": fields_renaming
        }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.post(f"/{self.tbl_name}/_rename_columns?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)
        
    def add_partitions(self, partitions: dict):
        """
                Add partitions to the current table.

                Args:
                    partitions (dict): A dictionary representing the partitions to be added.
                                    The dictionary should follow the format {"partitions": [{"name": "partition_name", ...}, ...]}.

                Returns:
                    bool: True if the addition of partitions is successful.

                Raises:
                    ValueError: If the addition process is not acknowledged, a ValueError exception is raised.
        """
        data = partitions
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.put(f"/{self.tbl_name}/_partitions?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)
        
    def delete_partitions(self, partition_names: list):
        """
                Delete specified partitions from the current table.

                Args:
                    partition_names (list): A list of partition names to be deleted.

                Returns:
                    bool: True if the deletion of partitions is successful.

                Raises:
                    ValueError: If the deletion process is not acknowledged, a ValueError exception is raised.
        """
        
        data = {}
        data["partition_names"] = partition_names
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.delete(f"/{self.tbl_name}/_partitions?database_name={self.tbl_meta.db_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)
    
# Define a function to handle type strings, returning the corresponding HippoType enumeration value or None
def _handle_type_str(type_str: str) -> Optional[HippoType]:
    lower_type_name = type_str.lower()
    for m in HippoType.__members__.values():
        if m.value == lower_type_name:
            return m
    for k, v in HippoTypeAliases.items():
        for alias in v:
            if lower_type_name == alias:
                return k
    return None


# Define a function to handle field schemas, returning a HippoField object or None
def _handle_field_schema(dd: dict) -> Optional[HippoField]:
    field_name = dd["name"]
    is_primary_key = dd["is_primary_key"]
    data_type = _handle_type_str(dd["data_type"])
    if dd.get('type_params', 'N') != "N":
        type_params = dd['type_params']
    else:
        type_params = {}
    if data_type is None:
        raise ValueError(f"value for data type error: {dd['data_type']}")
    return HippoField(name=field_name, is_primary_key=is_primary_key, data_type=data_type, type_params=type_params)


''' Define a HippoClient class '''


class HippoClient:
    # Initialization method, parameters include the hostname, username and password
    def __init__(self, host_port: str | list[str], username: str = 'shiva', pwd: str = 'shiva'):
        if isinstance(host_port, str):
            xx = [host_port]
        elif isinstance(host_port, list):
            xx = host_port
        else:
            raise TypeError("host_port should be str or list[str")
        self.hippo_conn = HippoConn(xx, username, pwd)

    # Define a method to handle table dictionaries, returning a HippoTable object or None
    def _handle_tbl_dict(self, tbl_name: str, dd: dict) -> Optional[HippoTable]:
        fields = [_handle_field_schema(x) for x in dd["schema"]["fields"]]

        auto_id = dd["schema"]["auto_id"]

        meta = HippoTableMeta(
            tbl_name=tbl_name,
            schema=fields,
            auto_id=auto_id,
            n_shards=dd["settings"]["number_of_shards"],
            n_replicas=dd["settings"]["number_of_shards"],
            db_name=dd["database_name"]
        )

        return HippoTable(self.hippo_conn, meta)

    # Define a method to check the table name
    def __check_single_tbl_name(self, tbl_name: str):
        assert '*' not in tbl_name, "table name should not contains *"

    # Define a method to check the database name
    def __check_single_database_name(self, database_name: str):
        assert '*' not in database_name, "database name should not contains *"

    # Define a method to copy tables
    def copy_table(self, source_table_name: str, dest_table_name: str,
                   source_database_name: str = "default", dest_database_name: str = "default",
                   remote_info: dict = None, fields: list = None, fields_projection: list = None,
                   expr: str = None, op_type: str = "insert", wait_for_completion=True, timeout: str = "2m"):

        """
                    Copy a table within a specified database.

                    Parameters:
                        source_table_name: The name of the source table.
                        dest_table_name: The name of the target table.
                        source_database_name: The name of the source database, default is "default".
                        dest_database_name: The name of the target database, default is "default".
                        remote_info: The dictionary of remote information to specify the remote source (optional).
                        fields: The list of fields to be copied (optional).
                        fields_projection: The list of field projections to modify the copied fields (optional).
                        expr: The expression to filter the data to be copied (optional).
                        op_type: The operation type, default is "insert", can be "insert", "update" or "upsert".
                        wait_for_completion: Whether to wait for the copy to complete, default is True.
                        timeout: Timeout, default is "2m".

                    Returns:
                        If the copy is successful, return the job status. Otherwise, raise a ValueError.
        """

        source_table = {
            "database_name": source_database_name,
            "table_name": source_table_name
        }

        if remote_info is not None:
            source_table["remote_info"] = remote_info

        dest_table = {
            "database_name": dest_database_name,
            "table_name": dest_table_name
        }

        data = {
            "source_table": source_table,
            "dest_table": dest_table,
            "op_type": op_type,
            "wait_for_completion": wait_for_completion,
            "timeout": timeout
        }

        if fields is not None:
            data["fields"] = fields

        if fields_projection is not None:
            data["fields_projection"] = fields_projection

        if expr is not None:
            data["expr"] = expr

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        if wait_for_completion:
            resp = self.hippo_conn.post(f"/_copy_by_query?pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"cannot copy table due to return error:{error_info}")

        else:
            resp = self.hippo_conn.post(f"/_copy_by_query?pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"cannot copy table due to return error:{error_info}")

    # Defines a method for fetching a table
    def get_table(self, tbl_name: str, database_name: str = "default") -> Optional[HippoTable]:

        """
                Fetches the specified table.

                Args:
                    tbl_name: Table name.
                    database_name: Database name, default is "default".

                Returns:
                    If found, returns an instance of HippoTable. Otherwise, returns None.
        """

        self.__check_single_tbl_name(tbl_name)
        resp = self.hippo_conn.get(f"/{tbl_name}?database_name={database_name}&pretty", js_data=None)
        r = HippoConn.handle_json_resp(resp)
        if len(r) < 1:
            return None
        else:
            for k, v in r.items():
                if k == tbl_name:
                    return self._handle_tbl_dict(k, v)
            return None

    # Defines a method for merging the main memory
    def compact_db(self, table_name: str, database_name: str = "default", wait_for_completion: bool = True,
                   timeout: str = "10m"):
        """
                Merges the main memory.

                Args:
                    tbl_name: Table name.
                    database_name: Database name, default is "default".
                    wait_for_completion: Whether to wait for the merge to complete, default is True.
                    timeout: Timeout, in seconds, default is 10m.

                Returns:
                    If the merge is successful, returns True. Otherwise, raises a ValueError exception.
        """

        req = {
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        sleep_time = 0.1  # initial sleep time
        max_sleep_time = 12.8  # max sleep time

        if wait_for_completion:
            while True:
                resp = self.hippo_conn.post(
                    f"/{table_name}/_compact_db?database_name={database_name}&pretty",
                    js_data=js)
                r = HippoConn.handle_json_resp(resp)
                st = r.get("job_status")

                if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                    return True
                elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                    error_info = None
                    try:
                        error_info = r.get("errors")
                    except:
                        pass
                    raise ValueError(f"build index return status: {st}, error info: {error_info}")

                time.sleep(sleep_time)  # wait for a while before next status check
                sleep_time = min(sleep_time * 2,
                                 max_sleep_time)  # double the sleep time but not more than the max value
        else:
            resp = self.hippo_conn.post(
                f"/{table_name}/_compact_db?database_name={database_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"build index return status: {st}, error info: {error_info}")

    # Defines a method for getting table information
    def get_table_info(self, tbl_name: str, database_name: str = "default"):

        """
                Fetches information about the specified table.

                Args:
                    tbl_name: Table name.
                    database_name: Database name, default is "default".

                Returns:
                    Returns a dictionary containing information about the table. Raises a ValueError exception if an error occurs.
        """

        resp = self.hippo_conn.get(f"/{tbl_name}?database_name={database_name}&pretty", js_data="")
        try:
            r = HippoConn.handle_json_resp(resp)
            return r
        except:
            raise ValueError(HippoConn.handle_json_resp(resp))

    # Defines a method for getting table structure
    def get_table_schema(self, tbl_name: str, database_name: str = "default"):

        """
                Fetches the structure of the specified table.

                Args:
                    tbl_name: Table name.
                    database_name: Database name, default is "default".

                Returns:
                    Returns a dictionary containing the structure of the table.
        """

        info = self.get_table_info(tbl_name, database_name)
        table_info = info.get(tbl_name, {})
        return table_info.get('schema', None)

    # Defines a method for getting vector indexes of the table
    def get_table_indexes(self, tbl_name: str, database_name: str = "default"):

        """
                Fetches the vector indexes of the specified table.

                Args:
                    tbl_name: Table name.
                    database_name: Database name, default is "default".

                Returns:
                    Returns a dictionary containing information about the vector indexes.
        """

        info = self.get_table_info(tbl_name, database_name)
        embedding_index_info = info.get(tbl_name, {})
        return embedding_index_info.get('embedding_indexes', None)

    # Defines a method for fetching the table configuration
    def get_table_config(self, table_name: str = None, database_name: str = "default"):

        """
                Fetches the configuration of the specified table.

                Args:
                    table_name: Table name, if not provided, fetches the configuration of all tables.
                    database_name: Database name, default is "default".

                Returns:
                    Returns a dictionary containing the table configuration. Raises a ValueError exception if the configuration is not found.
        """

        resp = None
        if table_name is None:
            resp = self.hippo_conn.get(f"/_settings?database_name={database_name}&pretty", js_data="")
        else:
            resp = self.hippo_conn.get(f"/{table_name}/_settings?database_name={database_name}&pretty", js_data="")
        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200:
            config_key = f"{database_name}#{table_name}"
            if config_key in r:
                return {table_name: r[config_key]}
            else:
                raise ValueError(f"No configuration found for table {table_name} in database {database_name}")
        else:
            raise ValueError(resp.content)

    # Defines a method for updating the table configuration
    def update_table_config(self, table_name: str, number_of_replicas: int = None, data_center: str = None,
                            tag: str = None,
                            embedding_segment_max_deletion_proportion: float = 0.1,
                            embedding_segment_seal_proportion: float = 0.2, embedding_segment_max_size_mb: int = 512,
                            tag_clear=True, disaster_preparedness=True, scatter_replica=True, dc_affinity=True,
                            database_name: str = "default"):

        """
                Updates the configuration of the specified table.

                Args:
                    table_name: Table name.
                    number_of_replicas, data_center, tag, embedding_segment_max_deletion_proportion, embedding_segment_seal_proportion, embedding_segment_max_size_mb, tag_clear, disaster_preparedness, scatter_replica, dc_affinity: Configuration options.
                    database_name: Database name, default is "default".

                Returns:
                    If the update is successful, returns True. Otherwise, raises a ValueError exception.
        """

        data = {
            "disaster_preparedness": disaster_preparedness,
            "scatter_replica": scatter_replica,
            "dc_affinity": dc_affinity,
            "tag.clear": tag_clear,
            "embedding.segment.max_size_mb": embedding_segment_max_size_mb,
            "embedding.segment.seal_proportion": embedding_segment_seal_proportion,
            "embedding.segment.max_deletion_proportion": embedding_segment_max_deletion_proportion
        }
        if number_of_replicas is not None:
            data["number_of_replicas"] = number_of_replicas
        if data_center is not None:
            data["data_center"] = data_center
        if tag is not None:
            data["tag"] = tag

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.put(f"/{table_name}/_settings?database_name={database_name}&pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200 and r.get("acknowledged") is True:
            return True
        else:
            raise ValueError(HippoConn.handle_json_resp(resp))

    def multi_search(self, patterns, database_name, output_fields: list, search_field, topk, vectors,
                     round_decimal: int = 2, only_explain: bool = False, **params):

        """
                Query the table according to the specified query parameters and return the result.

                Args:
                    patterns:  matching pattern
                    search_field: The name of the search field.
                    vectors: The list of vectors for search.
                    output_fields: The list of output fields.
                    topk: The maximum number of results to return.
                    round_decimal: decimal places to retain after scores defalut 2
                    only_explain: Whether to only execute explain defalut false
                    **params: Other query parameters.

                Returns:
                    Returns a list containing the query result.
        """

        req = {
            "output_fields": output_fields,
            "search_params": {
                "anns_field": search_field,
                "topk": topk,
                "params": params,
            },
            "vectors": vectors,
            "round_decimal": round_decimal,
            "only_explain": only_explain
        }

        js = json.dumps(req)
        js = json.loads(js)
        resp = self.hippo_conn.get(f"/{patterns}/_multi_search?database_name={database_name}&pretty", js_data=js)
        result = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200:
            return result
        else:
            return resp.content

    def compute_vector_distance(self, table_name: str, database_name: str, vector_field: str, primary_key_name: str,
                                primary_field: list, float_vectors: list[list], metric_type: MetricType):

        """
         Compute the vector distance between vectors in the specified table.

         Args:
             table_name (str): Name of the table.
             database_name (str): Name of the database.
             vector_field (str): Name of the vector field in the table.
             primary_key_name (str): Name of the primary key field.
             primary_field (list): List of primary field values.
             float_vectors (list[list]): List of float vectors to compare with.
             metric_type (MetricType): Type of distance metric to use.

         Returns:
             dict: The result of the vector distance computation.
         """

        req = {
            "vectors_left": {
                "database_name": database_name,
                "table_name": table_name,
                "field": vector_field,
                "primary_keys": [
                    {
                        "field_name": primary_key_name,
                        "field": primary_field
                    }
                ]
            },
            "vectors_right": {
                "float_vectors": float_vectors
            },
            "params": {
                "metric_type": metric_type.value
            }
        }

        js = json.dumps(req)
        js = json.loads(js)
        resp = self.hippo_conn.get(f"/_distance?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200:
            return r
        else:
            raise ValueError(resp.content)

    # Creates an alias for the given table in the specified database
    def create_alias(self, table_name: str, alise_name: str, database_name: str = "default"):

        """
                Creates an alias for the given table in the specified database.

                Args:
                    table_name: Table name.
                    alias_name: Alias name.
                    database_name: Database name, default is "default".

                Returns:
                    If the creation is successful, returns True. Otherwise, raises a ValueError exception.
        """

        actions = {
            "type": "Add",
            "database_name": database_name,
            "alias_name": alise_name,
            "table_name": table_name
        }

        data = {
            'actions': [actions]
        }

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.post(f"/_aliases?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200 and r.get("acknowledged") is True:
            return True
        else:
            raise ValueError(resp.content)

    # Deletes an alias in a specified database.
    def delete_alias(self, alias_name: str, database_name: str = "default"):

        """
                Deletes an alias in a specified database.

                Parameters:
                    alias_name: The alias.
                    database_name: The database name, default is "default".

                Returns:
                    If the deletion is successful, return True. Otherwise, throw a ValueError exception.
        """

        resp = self.hippo_conn.delete(f"/_aliases/{alias_name}?database_name={database_name}&pretty", js_data="")
        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200 and r.get("acknowledged") is True:
            return True
        else:
            raise ValueError(resp.content)

    # Creates a new database.
    def create_database(self,
                        name: str) -> bool:

        """
                Creates a new database.

                Parameters:
                    name: The name of the database.

                Returns:
                    If the creation is successful, return True. Otherwise, throw a ValueError exception.
        """

        data = {
            'database_name': name
        }

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.put(f"/_database?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200 and r.get("acknowledged") is True:
            return True
        else:
            raise ValueError(resp.content)

    # Lists all databases.
    def list_databases(self):
        """
                Lists all databases.

                Returns:
                    Return a list containing all databases.
        """

        resp = self.hippo_conn.get(f"/_database?pretty", js_data="")
        r = HippoConn.handle_json_resp(resp)
        return r

    # Deletes a specified database.
    def delete_database(self,
                        name: str) -> bool:
        """
                Deletes a specified database.

                Parameters:
                    name: The name of the database.

                Returns:
                    If deletion is successful, return True. Otherwise, throw a ValueError exception.
        """

        self.__check_single_database_name(name)
        data = {
            'database_name': name
        }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.delete(f"/_database?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if 'acknowledged' in r and r['acknowledged'] == True:
            return True
        else:
            raise ValueError(resp.content)

    # Lists data shards in a specified database (if a table name is provided, only the shards of that table are listed).
    def list_shards(self, table_name: str = None, database_name: str = "default"):

        """
                Lists data shards in a specified database. If a table name is provided, only the shards of that table are listed.

                Parameters:
                    table_name: The table name, if not provided, all table shards will be listed.
                    database_name: The database name, default is "default".

                Returns:
                    Return a dictionary containing shard information.
        """

        resp = None
        if table_name is None:
            resp = self.hippo_conn.get(f"/_cat/shards?database_name={database_name}&v", js_data="")
        else:
            resp = self.hippo_conn.get(f"/_cat/shards/{table_name}?database_name={database_name}&v", js_data="")

        if resp.status_code == 200:
            s = resp.content
            s_decoded = s.decode('utf-8')
            lines = s_decoded.split('\n')
            headers = lines[0].split()

            shards_data = {header: [] for header in headers}

            for line in lines[1:]:
                values = line.split()
                for header, value in zip(headers, values):
                    shards_data[header].append(value)
            return shards_data
        else:
            raise ValueError(HippoConn.handle_json_resp(resp))

    # Checks if a specified database contains a specified table.
    def check_table_exists(self, table_name: str, database_name: str = "default"):

        """
                Checks if a specified database contains a specified table.

                Parameters:
                    table_name: The table name.
                    database_name: The database name, default is "default".

                Returns:
                    If it exists, return True. Otherwise, return False.
        """

        data = {
            'database_name': database_name,
            'table_name': table_name
        }

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.get(f"/_check_table_existence?pretty", js_data=js)

        try:
            r = HippoConn.handle_json_resp(resp)
            if r.get("acknowledged"):
                return True
            else:
                return False
        except ValueError as e:
            raise f"restful error:{e}"

    def check_db_exists(self, database_name: str):

        """
                Checks if a specified database contains a specified table.

                Parameters:
                    database_name: The database name, default is "default".

                Returns:
                    If it exists, return True. Otherwise, return False.
        """

        data = {
            'database_name': database_name
        }

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.get(f"/_check_db_existence?pretty", js_data=js)

        try:
            r = HippoConn.handle_json_resp(resp)
            if r.get("acknowledged"):
                return True
            else:
                return False
        except ValueError as e:
            raise f"restful error:{e}"

    # Creates a new table in a specified database.
    def create_table(self,
                     name: str,
                     fields: list[HippoField],
                     auto_id: bool = False,
                     database_name: str = "default",
                     number_of_shards: int = 1,
                     number_of_replicas: int = 1,
                     partition_schema: dict = None
                     ) -> Optional[HippoTable]:

        """
                Creates a new table in a specified database.

                Parameters:
                    schema:
                        name: The table name.
                        fields: A list of HippoField objects, each representing a field.
                        auto_id: Whether to set an auto-incrementing primary key.
                        database_name: The database name, default is "default".
                    settings:
                        number_of_shards: The number of shards, default is 1.
                        number_of_replicas: The number of replicas, default is 1.
                    partition_shcema:
                        A dict of partition info

                Returns:
                    If creation is successful, return a HippoTable object. Otherwise, throw a ValueError exception.
        """
        fields_for_req = [asdict(f) for f in fields]

        data = {
            'settings': {
                'number_of_shards': number_of_shards,
                'number_of_replicas': number_of_replicas,
            },
            'schema': {
                'auto_id': auto_id,
                'fields': fields_for_req,
            }
        }
        if partition_schema != None:
            data['partition_schema'] = partition_schema
        

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.put(f"/{name}?database_name={database_name}&pretty", js_data=js)

        r = HippoConn.handle_json_resp(resp)
        if resp.status_code == 200 and r.get("acknowledged") is True:
            meta = HippoTableMeta(tbl_name=name, auto_id=auto_id, schema=fields, n_replicas=number_of_replicas,
                                  n_shards=number_of_shards, db_name=database_name)
            return HippoTable(hippo_conn=self.hippo_conn, tbl_meta=meta)
        else:
            raise ValueError(resp.content)

    # Renames a table in a specified database.
    def rename_table(self, old_table_name: str, new_table_name: str, database_name: str = "default"):

        """
                Renames a table in a specified database.

                Parameters:
                    old_table_name: The old table name.
                    new_table_name: The new table name.
                    database_name: The database name, default is "default".

                Returns:
                    If renaming is successful, return True. Otherwise, throw a ValueError exception.
        """

        data = {
            "database_name": database_name,
            "table_name": old_table_name,
            "new_table_name": new_table_name
        }

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.put(f"/_rename_table?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)

        if resp.status_code == 200 and r.get("acknowledged") is True:
            return True
        else:
            raise ValueError(resp.content)

    # Deletes a table in a specified database.
    def delete_table(self, tbl_name: str, database_name: str = "default"):

        """
                Deletes a table in a specified database.

                Parameters:
                    tbl_name: The name of the table to be deleted.
                    database_name: The database name, default is "default".

                Returns:
                    If deletion is successful, return True. Otherwise, throw a ValueError exception.
        """

        self.__check_single_tbl_name(tbl_name)
        resp = self.hippo_conn.delete(f"/{tbl_name}?database_name={database_name}&pretty", js_data=None, headers=None)
        r = HippoConn.handle_json_resp(resp)
        if 'acknowledged' in r and r['acknowledged'] == True:
            return True
        else:
            raise ValueError(resp.content)

    # Lists all tables in a specified database.
    def list_tables(self, database_name: str = "default", pattern: str = "*", ignore_aliases=True):

        """
                Lists all tables in a specified database.

                Parameters:
                    database_name: The database name, default is "default".
                    pattern: The matching pattern for table names, default is "*", matching all tables.
                    ignore_aliases: Whether to ignore aliases, default is True.

                Returns:
                    Returns a dictionary containing information of all tables that match the pattern.
        """

        ignore_aliases = str(ignore_aliases).lower()
        if pattern == "*":
            resp = self.hippo_conn.get(f"/_cat/tables?database_name={database_name}&v&ignore_aliases={ignore_aliases}",
                                       js_data="")
        else:
            resp = self.hippo_conn.get(
                f"/_cat/tables/{pattern}?database_name={database_name}&v&ignore_aliases={ignore_aliases}", js_data="")

        if resp.status_code == 200:
            s = resp.content
            s_decoded = s.decode('utf-8')
            lines = s_decoded.split('\n')
            headers = lines[0].split()
            table_data = {header: [] for header in headers}

            for line in lines[1:]:
                values = line.split()
                for header, value in zip(headers, values):
                    table_data[header].append(value)
            return table_data
        else:
            raise ValueError(HippoConn.handle_json_resp(resp))

    # This method is used to create a new user. You can specify the username, password, and set whether the user has superuser privileges, can create roles, and databases.
    def create_user(self, user_name: str,
                    pwd: str,
                    is_super: bool = False,
                    can_create_role: bool = False,
                    can_create_db: bool = False) -> bool:

        """
                Creates a new user.

                Parameters:
                    user_name: The username.
                    pwd: The password.
                    is_super: Whether the user is a superuser, default is False.
                    can_create_role: Whether the user can create roles, default is False.
                    can_create_db: Whether the user can create databases, default is False.

                Returns:
                    Returns a boolean value indicating whether the operation was successful.
        """

        data = {
            "password": pwd,
            "metadata": {
                "is_super": is_super,
                "can_create_role": can_create_role,
                "can_create_db": can_create_db
            }
        }

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.put(f"/_security/user/{user_name}?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("created"):
            return True
        else:
            raise ValueError(r)

    # Deletes a specified user.
    def delete_user(self, user_name: str):
        """
                Deletes a specified user.

                Parameters:
                    user_name: The username of the user to be deleted.

                Returns:
                    Returns a boolean value indicating whether the operation was successful.
        """

        resp = self.hippo_conn.delete(f"/_security/user/{user_name}?pretty", js_data="")
        r = HippoConn.handle_json_resp(resp)
        if r.get("found"):
            return True
        else:
            raise ValueError(r)

    # Retrieves information about a specified user.
    def get_user_info(self, user_name: str):
        """
                Retrieves information about a specified user.

                Parameters:
                    user_name: The username.

                Returns:
                    Returns a dictionary containing the user's information.
        """

        resp = self.hippo_conn.get(f"/_security/user/{user_name}?pretty", js_data="")
        r = HippoConn.handle_json_resp(resp)
        return r

    # Changes information about a specified user, including the password and metadata (such as whether the user is a superuser, can create roles, and databases). You can choose whether to change the metadata.
    def change_user_info(self, user_name: str,
                         pwd: str,
                         change_meta: bool = False,
                         is_super: bool = False,
                         can_create_role: bool = False,
                         can_create_db: bool = False):
        """
                Changes information about a specified user, including the password and metadata (such as whether the user is a superuser, can create roles, and databases).

                Parameters:
                    user_name: The username.
                    pwd: The new password.
                    change_meta: Whether to change the metadata, default is False.
                    is_super: Whether the user is a superuser, default is False.
                    can_create_role: Whether the user can create roles, default is False.
                    can_create_db: Whether the user can create databases, default is False.

                Returns:
                    Returns a boolean value indicating whether the operation was successful.
        """

        data = {
            "password": pwd,
            "metadata": {
                "is_super": is_super,
                "can_create_role": can_create_role,
                "can_create_db": can_create_db
            }
        }
        if not change_meta:
            del data["metadata"]

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.put(f"/_security/user/{user_name}/_alter?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)

    # Changes the password of a specified user. If no username is provided, the password of the current user will be changed.
    def change_password(self, new_password: str, user_name: str = None):
        """
                Changes the password of a specified user. If no username is provided, the password of the current user will be changed.

                Parameters:
                    new_password: The new password.
                    user_name: The username. If None, the password of the current user will be changed.

                Returns:
                    A boolean value indicating whether the operation was successful.
        """

        if user_name is None:
            return self.change_user_info(self.hippo_conn.username, new_password)
        else:
            return self.change_user_info(user_name, new_password)

    # Grants a specified user permission on a specific database or table.
    def grant_user_permission(self, user_name: str, privileges: list[str], table_name: str = None,
                              database_name: str = "default"):

        """
                Grants a specified user permission on a specific database or table.

                Parameters:
                    user_name: The username.
                    privileges: The list of privileges.
                    table_name: The table name. If None, grants permission to the entire database.
                    database_name: The database name, default is "default".

                Returns:
                    A boolean value indicating whether the operation was successful.
        """

        data = None
        if table_name is None:
            data = {
                "database_name": database_name,
                "privileges": privileges
            }
        else:
            data = {
                "table_name": table_name,
                "database_name": database_name,
                "privileges": privileges
            }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.post(f"/_security/acl/{user_name}?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)

    # Deletes the permissions of a specified user on a specific database or table.
    def delete_user_permission(self, user_name: str, privileges: list[str], table_name: str = None,
                               database_name: str = "default"):

        """
                Deletes the permissions of a specified user on a specific database or table.

                Parameters:
                    user_name: The username.
                    privileges: The list of permissions.
                    table_name: The table name. If None, deletes permissions for the entire database.
                    database_name: The database name, default is "default".

                Returns:
                    A boolean value indicating whether the operation was successful.
        """

        data = None
        if table_name is None:
            data = {
                "database_name": database_name,
                "privileges": privileges
            }
        else:
            data = {
                "table_name": table_name,
                "database_name": database_name,
                "privileges": privileges
            }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.delete(f"/_security/acl/{user_name}?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)

    # Used to view the permissions of a specified user
    def view_user_permission(self, user_name: str):
        """
                View the permissions of a specified user.

                Parameters:
                    user_name: The username.

                Return:
                    A dictionary containing the user's permission information.
        """

        resp = self.hippo_conn.get(f"/_security/user/_privileges/{user_name}?pretty", js_data="")
        if resp.status_code == 200:
            r = HippoConn.handle_json_resp(resp)
            return r
        else:
            raise ValueError(HippoConn.handle_json_resp(resp))

    # Used to view the permissions of a specific table
    def view_table_permission(self, table_name: str, database_name: str = "default"):
        """
                View the permissions of a specified table.

                Parameters:
                    table_name: The table name.
                    database_name: The database name, default is "default".

                Return:
                    A dictionary containing the table's permission information.
        """

        resp = self.hippo_conn.get(f"/_security/tables/{table_name}?database_name={database_name}&pretty", js_data="")
        if resp.status_code == 200:
            r = HippoConn.handle_json_resp(resp)
            return r
        else:
            raise ValueError(HippoConn.handle_json_resp(resp))

    # Lists all tables
    def list_all_tables(self) -> list[HippoTable]:
        """
                List all tables.

                Return:
                    A list of HippoTable objects, each representing a table.
        """

        resp = self.hippo_conn.get("/_settings?pretty", js_data=None)
        r = HippoConn.handle_json_resp(resp)
        ret = []
        for db_tbl_name, content in r.items():
            xx = db_tbl_name.split("#")
            db, tbl = xx[0], xx[1]
            tbl_meta = HippoTableMeta(tbl, None, int(content["number_of_replicas"]), int(content["number_of_shards"]),
                                      db_name=db)
            ret.append(HippoTable(self.hippo_conn, tbl_meta))
        return ret

    # Used to get jobs. You can specify the job ID and operation mode through parameters.
    def get_job(self, job_ids: list[str] = None, action_patterns=None):
        """
                Get jobs that match the specified action pattern and are in the given job ID list.

                Parameters:
                    job_ids: A list of specified job IDs, default is None, which means getting all jobs.
                    action_patterns: Specified action patterns, default is ["hippo*"].

                Return:
                    A dictionary containing the information of the fetched jobs.
        """

        if action_patterns is None:
            action_patterns = ["hippo*"]

        data = {
            "action_patterns": action_patterns
        }

        if job_ids is not None:
            data["job_jds"] = job_ids

        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)

        resp = self.hippo_conn.get("/_jobs?pretty", js_data=js)

        if resp.status_code == 200:
            return HippoConn.handle_json_resp(resp)
        else:
            raise ValueError(HippoConn.handle_json_resp(resp))

    # Deletes the specified job.
    def delete_job(self, job_id: str):
        """
                Delete the job with the specified ID.

                Parameters:
                    job_id: The ID of the job to be deleted.

                Return:
                    A boolean value indicating whether the operation was successful.
        """

        resp = self.hippo_conn.delete(f"/_jobs/{job_id}?pretty", js_data="")
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)

    # View tables in the recycle bin
    def view_tables_in_trash(self, database_name: str = "default"):
        """
                Query and return the information of the tables in the recycle bin in the specified database.

                Parameters:
                    database_name: The database name, default is "default".

                Return:
                    A dictionary in which the keys are table attributes and the values are lists corresponding to the attributes.
        """

        resp = self.hippo_conn.get(f"/_cat/trash?database_name={database_name}&v", js_data="")
        if resp.status_code == 200:
            s = resp.content
            s_decoded = s.decode('utf-8')
            lines = s_decoded.split('\n')
            headers = lines[0].split()

            table_data = {header: [] for header in headers}

            for line in lines[1:]:
                values = line.split()
                for header, value in zip(headers, values):
                    table_data[header].append(value)
            return table_data
        else:
            raise ValueError(HippoConn.handle_json_resp(resp))

    # Deletes a specified table from the recycle bin
    def delete_table_in_trash(self, table_name: str, database_name: str = "default"):
        """
                Deletes a specified table from the trash of a specified database.

                Parameters:
                    table_name: The name of the table to be deleted.
                    database_name: The name of the database, default is "default".

                Returns:
                    A boolean value indicating whether the operation was successful.
        """

        resp = self.hippo_conn.delete(f"/_trash/{table_name}?database_name={database_name}&pretty", js_data="")
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)
    
    def table_open(self, pattern, database_name: str = "default"):
        """
                Open a table with the specified pattern in the specified database.

                Args:
                    pattern (str): The pattern of the table to be opened.
                    database_name (str): The name of the database where the table is located (default is 'default').

                Returns:
                    bool: True if the table is successfully opened.

                Raises:
                    ValueError: If the opening process is not acknowledged, a ValueError exception is raised.
        """
        data = {
            "database_name": database_name
        }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.post(f"/{pattern}/_open?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)
        
    def table_close(self, pattern, database_name: str = "default"):
        """
                Close a table with the specified pattern in the specified database.

                Args:
                    pattern (str): The pattern of the table to be closed.
                    database_name (str): The name of the database where the table is located (default is 'default').

                Returns:
                    bool: True if the table is successfully closed.

                Raises:
                    ValueError: If the closing process is not acknowledged, a ValueError exception is raised.
        """
        data = {
            "database_name": database_name
        }
        js = json.dumps(data, cls=HippoTypesEncoder)
        js = json.loads(js)
        resp = self.hippo_conn.post(f"/{pattern}/_close?pretty", js_data=js)
        r = HippoConn.handle_json_resp(resp)
        if r.get("acknowledged"):
            return True
        else:
            raise ValueError(r)
    
    def warmup_db(self, table_name: str, database_name: str = "default", wait_for_completion: bool = True,
                   timeout: str = "10m"):
        """
                Warm up the specified Elasticsearch table.

                Args:
                    table_name (str): The name of the table to be warmed up.
                    database_name (str): The name of the database where the table is located (default is 'default').
                    wait_for_completion (bool): Whether to wait for the warm-up process to complete (default is True).
                    timeout (str): The maximum time to wait for the warm-up process (default is '10m').

                Returns:
                    bool: True if the warm-up process is successful.

                Raises:
                    ValueError: If the warm-up process is not successful, a ValueError exception is raised.
        """
        req = {
            "wait_for_completion": wait_for_completion,
            "timeout": timeout,
        }

        js = json.dumps(req)
        js = json.loads(js)

        sleep_time = 0.1  # initial sleep time
        max_sleep_time = 12.8  # max sleep time

        if wait_for_completion:
            while True:
                resp = self.hippo_conn.post(
                    f"/{table_name}/_warmup_db?database_name={database_name}&pretty",
                    js_data=js)
                r = HippoConn.handle_json_resp(resp)
                st = r.get("job_status")

                if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                    return True
                elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                    error_info = None
                    try:
                        error_info = r.get("errors")
                    except:
                        pass
                    raise ValueError(f"build index return status: {st}, error info: {error_info}")

                time.sleep(sleep_time)  # wait for a while before next status check
                sleep_time = min(sleep_time * 2,
                                 max_sleep_time)  # double the sleep time but not more than the max value
        else:
            resp = self.hippo_conn.post(
                f"/{table_name}_warmup_db?database_name={database_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"build index return status: {st}, error info: {error_info}")
    
    def drop_block_cache(self, node=None):
        """
                Drop the block cache in Elasticsearch.

                Args:
                    node (str): The name of the node where the block cache should be dropped (optional).

                Returns:
                    dict: The response data.

                Raises:
                    None
        """
        if node==None:
            resp = self.hippo_conn.post(f"/_drop_block_cache?pretty", js_data="")
        else:
            resp = self.hippo_conn.post(f"/_drop_block_cache/{node}?pretty&drop_index_block_cache=true", js_data="")
        r = HippoConn.handle_json_resp(resp)
        return r
        
    def analyze_database(self, table_name: str, is_update: bool = False, column_names: list = [], 
                         database_name: str = "default", wait_for_completion: bool = True, timeout: str = "10m"):
        """
                Analyze the specified Elasticsearch table.

                Args:
                    table_name (str): The name of the table to be analyzed.
                    is_update (bool): Whether to trigger the construction of statistics information (default is False).
                    column_names (list): List of columns for which to view statistics information (default is an empty list; effective only when is_update is False).
                    database_name (str): The name of the database where the table is located (default is 'default').
                    wait_for_completion (bool): Whether to wait for the analysis process to complete (default is True).
                    timeout (str): The maximum time to wait for the analysis process (default is '10m').

                Returns:
                    bool: True if the analysis process is successful.

                Raises:
                    ValueError: If the analysis process is not successful, a ValueError exception is raised.
        """
        req = {
            "is_update" : is_update,
            "columns" : column_names,
            "wait_for_completion" : wait_for_completion,
            "timeout" : timeout
        }
        js = json.dumps(req)
        js = json.loads(js)

        sleep_time = 0.1  # initial sleep time
        max_sleep_time = 12.8  # max sleep time

        if wait_for_completion:
            while True:
                resp = self.hippo_conn.post(
                    f"/{table_name}/_analyze_db?database_name={database_name}&pretty",
                    js_data=js)
                r = HippoConn.handle_json_resp(resp)
                st = r.get("job_status")

                if st == HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                    return True
                elif st is None or st != HippoJobStatus.HIPPO_JOB_SUCCESS.value:
                    error_info = None
                    try:
                        error_info = r.get("errors")
                    except:
                        pass
                    raise ValueError(f"build index return status: {st}, error info: {error_info}")

                time.sleep(sleep_time)  # wait for a while before next status check
                sleep_time = min(sleep_time * 2,
                                 max_sleep_time)  # double the sleep time but not more than the max value
        else:
            resp = self.hippo_conn.post(
                f"/{table_name}_analyze_db?database_name={database_name}&pretty", js_data=js)
            r = HippoConn.handle_json_resp(resp)
            st = r.get("job_status")

            if st == HippoJobStatus.HIPPO_JOB_INVALID.value:
                return True
            elif st is None or st != HippoJobStatus.HIPPO_JOB_INVALID.value:
                error_info = None
                try:
                    error_info = r.get("errors")
                except:
                    pass
                raise ValueError(f"build index return status: {st}, error info: {error_info}")
