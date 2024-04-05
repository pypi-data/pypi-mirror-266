from typing import Optional
from cgc.commands.compute.compute_utills import list_get_mounted_volumes
import cgc.utils.consts.env_consts as env_consts


def job_delete_payload(name):
    """
    Create payload for job delete.
    """
    payload = {
        "name": name,
    }
    return payload


def job_create_payload(
    name,
    cpu,
    memory,
    volumes: list,
    volume_full_path: str,
    resource_data: list = [],
    config_maps_data: list = [],
    gpu: int = 0,
    gpu_type: str = None,
    shm_size: int = 0,
    image_name: str = "",
    startup_command: str = "",
    repository_secret: str = "",
    ttl_seconds_after_finished: Optional[int] = None,
):
    """
    Create payload for app creation.
    """
    extra_payload = {}
    if shm_size is not None and shm_size != 0:
        extra_payload["shared_memory"] = shm_size

    if ttl_seconds_after_finished is not None:
        extra_payload["ttl_seconds_after_finished"] = ttl_seconds_after_finished

    payload = {
        "resource_data": {
            "name": name,
            "cpu": cpu,
            "gpu": gpu,
            "memory": memory,
            "gpu_type": gpu_type,
            "full_mount_path": volume_full_path,
            **extra_payload,
        }
    }
    try:
        if len(volumes) != 0:
            if not volume_full_path:
                payload["resource_data"]["pv_volume"] = volumes
            elif volume_full_path and len(volumes) != 1:
                raise Exception(
                    "Volume full path can only be used with a single volume"
                )
            else:
                payload["resource_data"]["pv_volume"] = volumes
    except TypeError:
        pass
    try:
        resource_data_dict = {"resource_data": {}}
        if len(resource_data) != 0:
            for resource in resource_data:
                try:
                    key, value = resource.split("=")
                    resource_data_dict["resource_data"][key] = value
                except ValueError:
                    raise Exception(
                        "Invalid resource data format. Use key=value format"
                    )
        if image_name:
            resource_data_dict["resource_data"]["custom_image"] = image_name
        if startup_command:
            resource_data_dict["resource_data"]["custom_command"] = startup_command
        if repository_secret:
            resource_data_dict["resource_data"][
                "image_pull_secret_name"
            ] = repository_secret
        if resource_data_dict["resource_data"] != {}:
            payload["template_specific_data"] = resource_data_dict
    except TypeError:
        pass
    try:
        if len(config_maps_data) != 0:
            config_maps_data_dict = {}
            for config_map in config_maps_data:
                try:
                    key, value = config_map.split(
                        "="
                    )  # where key is name of config map and value is data
                    config_maps_data_dict[key] = (
                        value  # value is dict, ex.: {"key": "value"}
                    )
                except ValueError:
                    raise Exception(
                        "Invalid config map data format. Use key=value format"
                    )
            payload["config_maps_data"] = config_maps_data_dict
    except TypeError:
        pass
    return payload


def get_job_list(job_pod_list: list, job_list: list):
    list_of_json_data = get_job_pod_list(job_pod_list)
    for json_data in list_of_json_data:
        for job in job_list:
            if job.get("name") == json_data.get("name"):
                json_data["ttl_seconds_after_finished"] = job.get(
                    "ttl_seconds_after_finished", "N/A"
                )
                break
    return list_of_json_data


def get_job_pod_list(job_pod_list: list) -> list:
    """Formats and returns list of jobs to print.

    :param pod_list: list of pods
    :type pod_list: list
    :return: formatted list of apps
    :rtype: list
    """
    output_data = []

    for pod in job_pod_list:
        try:
            main_container_name = "custom-job"
            try:
                main_container = [
                    x
                    for x in pod.get("containers", [])
                    if x.get("name") == main_container_name
                ][0]
            except IndexError:
                raise Exception(
                    "Parser was unable to find main container in server output in container list"
                )
            volumes_mounted = list_get_mounted_volumes(main_container.get("mounts", []))
            limits = main_container.get("resources", {}).get("limits")
            cpu = limits.get("cpu") if limits is not None else 0
            ram = limits.get("memory") if limits is not None else "0Gi"

            pod_data = {
                "name": pod.get("labels", {}).get("app-name"),
                "status": pod.get("status", {}),
                "volumes_mounted": volumes_mounted,
                "cpu": cpu,
                "ram": ram,
                "gpu-count": pod.get("labels", {}).get("gpu-count", 0),
                "gpu-label": pod.get("labels", {}).get("gpu-label", "N/A"),
            }
            # getting rid of unwanted and used values
            if "pod-template-hash" in pod["labels"].keys():
                pod["labels"].pop("pod-template-hash")
            pod["labels"].pop("app-name")
            pod["labels"].pop("entity")
            pod["labels"].pop("resource-type")
            pod["labels"].pop("job-name")
            pod["labels"].pop("controller-uid")
            pod["labels"].pop("api-key-id", None)
            pod["labels"].pop("user-id", None)

            # appending the rest of labels
            pod_data.update(pod["labels"])
            output_data.append(pod_data)
        except KeyError:
            pass

    return output_data
