from tabulate import tabulate
from cgc.utils.message_utils import key_error_decorator_for_helpers


@key_error_decorator_for_helpers
def cgc_status_response(data: dict):
    """Generates and prints resource limits and available resources in a pretty format

    :param data: data to extrct resources from
    :type data: dict
    :param metric_error: error metric for graphana
    :type metric_error: str
    """

    resources_available = data["details"]["available_resources"]
    resources_limits = data["details"]["limits_resources"]
    list_headers = ["Resource", "Type", "Available", "Limit"]
    resource_names = [
        "CPU",
        "RAM",
        "GPU",
        "-",
        "-",
        # "-",
        "Volume",
        "Storage",
        "-",
        "-",
    ]
    types = [
        "",
        "",
        "",
        "A100",
        "A5000",
        # "V100",
        "Count",
        "",
        "nvme",
        "ssd",
    ]
    resource_keys = [
        "requests.cpu",
        "requests.memory",
        "requests.nvidia.com/gpu",
        "requests.comtegra.cloud/a100",
        "requests.comtegra.cloud/a5000",
        # "requests.comtegra.cloud/v100",
        "persistentvolumeclaims",
        "requests.storage",
        "nvme-rwx.storageclass.storage.k8s.io/requests.storage",
        "ssd-rwx.storageclass.storage.k8s.io/requests.storage",
    ]

    resources_available_list = []
    resources_limits_list = []
    for key in resource_keys:
        available = resources_available[key]
        limit = resources_limits[key]
        if "storage" in key or "memory" in key:
            available = f"{available} Gb"
            limit = f"{limit} Gb"
        else:
            available = int(available)
            limit = int(limit)
        resources_available_list.append(available)
        resources_limits_list.append(limit)

    return tabulate(
        list(
            zip(resource_names, types, resources_available_list, resources_limits_list)
        ),
        headers=list_headers,
    )


def cgc_logs_response(data: dict):
    return "\n".join(
        "==> %s/%s <==\n%s" % (pod, cont, log)
        for pod, containers in data["details"]["logs"].items()
        for cont, log in containers.items()
    )
