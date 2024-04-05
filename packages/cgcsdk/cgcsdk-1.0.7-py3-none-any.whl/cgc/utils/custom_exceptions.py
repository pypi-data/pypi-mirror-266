########### custom exceptions dict #############
# warnings are divided by code, then by reason
# every warning has its message that will be returned to print
CUSTOM_EXCEPTIONS = {
    500: {
        "UNDEFINED": "undefined exception",
    },
    413: {
        "PVC_CREATE_STORAGE_LIMIT_EXCEEDED": "This request exceeds your storage limits",
        "PVC_CREATE_NOT_ENOUGH_STORAGE_IN_CLUSTER": "No more storage available",
        "REQUEST_RESOURCE_LIMIT_EXCEEDED": "This request exceeds your resources limit",
        "RESOURCES_NOT_AVAILABLE_IN_CLUSTER": "Requested resources not available",
    },
    409: {
        "PVC_NAME_ALREADY_EXISTS": "Volume with this name already exists.",
        "PVC_DELETE_EXCEPTION": "Can't delete mounted volume, try with force",
        "RESOURCE_PORTS_ALREADY_EXISTS": "Port with this name already exists.",
        "RESOURCE_TEMPLATE_NAME_ALREADY_EXISTS": "Resource with this name already exists.",
        "JOB_CREATE_ALREADY_EXISTS": "Job with this name already exists.",
    },
    404: {
        "PVC_CREATE_NO_SC": "Selected disk type and access mode unavailable",
        "BILLING_STATUS_NO_DATA": "No data to print.",
        "NOT_DELETED_ANYTHING_IN_COMPUTE_DELETE": "No app with this name to delete.",
        "API_KEY_DELETE_ERROR": "No api key with this id to delete",
        "PVC_MOUNT_NOT_FOUND_TEMPLATE": "No app with this name to mount.",
        "PVC_UNMOUNT_NOT_MOUNTED": "Volume with this name is not mounted.",
        "PVC_NOT_FOUND": "Volume with this name not found.",
        "PVC_DELETE_NOT_FOUND": "App with this name not found.",
        "COMPUTE_RESTART_TEMPLATE_NOT_FOUND": "App with this name not found.",
        "COMPUTE_CREATE_TEMPLATE_NOT_FOUND": "There is no template with this name.",
        "COMPUTE_TEMPLATE_NAME_NOT_FOUND": "No app with this name.",
        "COMPUTE_RESOURCE_QUOTA_NOT_FOUND": "You do not have enforced limits on your namespace.",
        "JOB_NOT_FOUND": "Job with this name not found.",
        "RESOURCE_NOT_FOUND": "Resource with this name not found.",
    },
    400: {
        "WRONG_DATE_FORMAT": "Wrong date format.",
        "ENTITY_NOT_ALLOWED": "You can't create this entity.",
        "PVC_MOUNT_ALREADY_MOUNTED": "This volume is already mounted.",
        "TEMPLATE_NAME_SYSTEM_RESERVED": "You can't create app with this name.",
        "JOB_LACKS_REQUIRED_PARAMETER": "Job requires container image parameter.",
    },
}
