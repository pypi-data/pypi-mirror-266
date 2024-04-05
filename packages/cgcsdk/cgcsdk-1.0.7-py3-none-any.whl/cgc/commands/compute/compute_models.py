from enum import Enum


class CGCEntityList(Enum):
    """Base class for other lists"""

    @classmethod
    def get_list(cls) -> list[str]:
        return [el.value for el in cls]


class ComputesList(CGCEntityList):
    """List of templates in cgc-server

    :param Enum: name of template
    :type Enum: str
    """

    NVIDIA_TENSORFLOW = "nvidia-tensorflow"
    NVIDIA_RAPIDS = "nvidia-rapids"
    NVIDIA_PYTORCH = "nvidia-pytorch"
    NVIDIA_TRITON = "nvidia-triton"
    NGINX = "nginx"
    LABEL_STUDIO = "label-studio"
    COMFY_UI = "comfy-ui"
    RAG = "rag"
    DEEPSTREAM = "deepstream"
    T2V_TRANSFORMERS = "t2v-transformers"
    CUSTOM = "custom"


class DatabasesList(CGCEntityList):
    """List of templates in cgc-server

    :param Enum: name of template
    :type Enum: str
    """

    MONGODB = "mongodb"
    POSTGRESQL = "postgresql"
    REDIS = "redis"
    WEAVIATE = "weaviate"
    # MINIO = "minio"


class GPUsList(CGCEntityList):
    """List of templates in cgc-server

    :param Enum: name of template
    :type Enum: str
    """

    V100 = "V100"
    A100 = "A100"
    A5000 = "A5000"
    H100 = "H100"
    P40 = "P40"
    P100 = "P100"
