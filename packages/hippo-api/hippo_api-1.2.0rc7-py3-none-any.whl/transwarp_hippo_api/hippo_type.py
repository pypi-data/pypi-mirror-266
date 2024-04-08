import json
import types
from enum import Enum

from typing import List, Dict


class HippoType(Enum):
    INT8 = "int8"
    INT16 = "int16"
    INT32 = "int32"
    INT64 = "int64"
    FLOAT = "float"
    DOUBLE = "double"
    BOOL = "bool"
    STRING = "string"
    CHAR = "char"
    VARCHAR = "varchar"
    VARCHAR2 = "varchar2"
    DATE = "date"
    TIMESTAMP = "timestamp"
    DATETIME = "datetime"
    TIME = "time"
    FLOAT_VECTOR = "float_vector"
    BINARY_VECTOR = "binary_vector"
    SPARSE_FLOAT_VECTOR = "sparse_float_vector"
    ARRAY = "array"


HippoTypeAliases = types.MappingProxyType({
    HippoType.INT64: ["bigint"]
})

HippoVector = List[float]
DataVector = list
HippoResult = Dict[str, DataVector]


class HippoTypesEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, HippoType):
            return obj.value
        return super().default(obj)


class HippoJobStatus(Enum):
    HIPPO_JOB_PENDING = "SHIVA_JOB_PENDING"
    HIPPO_JOB_RUNNING = "SHIVA_JOB_RUNNING"
    HIPPO_JOB_CANCELED = "SHIVA_JOB_CANCELED"
    HIPPO_JOB_FAILED = "SHIVA_JOB_FAILED"
    HIPPO_JOB_SUCCESS = "SHIVA_JOB_SUCCESS"
    HIPPO_JOB_INVALID = "SHIVA_JOB_INVALID"


class IndexType(Enum):
    FLAT = "FLAT"
    IVF_FLAT = "IVF_FLAT"
    IVF_SQ = "IVF_SQ"
    IVF_PQ = "IVF_PQ"
    IVF_PQ_FS = "IVF_PQ_FS"
    HNSW = "HNSW"
    ANNOY = "ANNOY"
    BIN_IVF = "BIN_IVF"
    BIN_FLAT = "BIN_FLAT"
    BIN_HNSW = "BIN_HNSW"
    SPARSE_HNSW = "SPARSE_HNSW"


class MetricType(Enum):
    L2 = "l2"
    IP = "ip"
    COSINE = "cosine"
