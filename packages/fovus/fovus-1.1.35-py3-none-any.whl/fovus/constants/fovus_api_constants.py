# API
from enum import Enum

from fovus.constants.cli_constants import CPU, GPU, GPU_INTERNAL_REPRESENTATION

COGNITO_REGION = "us-east-1"
TIMEOUT_SECONDS = 10
DEFAULT_TIMEZONE = "UTC"


# API: Access through FovusApiUtil.get_api_address function to allow domain override via CLI.
class Api(Enum):
    JOB = "job"
    FILE = "file"
    SOFTWARE = "software"
    BENCHMARK = "benchmark"
    WORKSPACE = "workspace"
    LICENSE = "license"


class ApiMethod(Enum):
    CREATE_JOB = "create-job"
    CREATE_ZOMBIE_JOB_CHECK_SCHEDULER = "create-zombie-job-check-scheduler"
    GET_JOB_INFO = "get-job-info"
    GET_FILE_DOWNLOAD_TOKEN = "get-file-download-token"  # nosec
    GET_FILE_UPLOAD_TOKEN = "get-file-upload-token"  # nosec
    LIST_SOFTWARE = "list-software"
    LIST_LICENSES = "list-licenses"
    LIST_SOFTWARE_LICENSE_RELATIONSHIPS = "list-software-license-relationships"
    LIST_BENCHMARK_PROFILE = "list-benchmark-profile"
    LIST_WORKSPACES = "list-workspaces"
    GET_LICENSE_CONSUMPTION_PROFILE = "get-license-consumption-profiles"
    DELETE_JOB = "delete-job"
    GET_MOUNT_STORAGE_CREDENTIALS = "get-mount-storage-credentials"


# Benchmarking
BOUND_VALUE_CORRECTION_PRINT_ORDER = (
    "minvCpu",
    "maxvCpu",
    "minvCpuMemGiB",
    "minGpu",
    "maxGpu",
    "minGpuMemGiB",
    "parallelismOptimization",
    "scalableParallelism",
)
COMPUTING_DEVICE_TO_BP_COMPUTING_DEVICE = {
    CPU: CPU,
    GPU: GPU_INTERNAL_REPRESENTATION,
}

# Payload
AUTHORIZATION_HEADER = "Authorization"
CONTAINERIZED = "containerized"
ENVIRONMENT = "environment"
LICENSE_ADDRESS = "licenseAddress"
LICENSE_NAME = "licenseName"
LICENSE_COUNT_PER_TASK = "licenseCountPerTask"
LICENSE_CONSUMPTION_PROFILE_NAME = "licenseConsumptionProfileName"
LICENSE_FEATURE = "licenseFeature"
MONOLITHIC_LIST = "monolithicList"
PAYLOAD_CONSTRAINTS = "constraints"
PAYLOAD_OBJECTIVE = "objective"
PAYLOAD_JOB_CONSTRAINTS = "jobConstraints"
PAYLOAD_JOB_NAME = "jobName"
PAYLOAD_TASK_CONSTRAINTS = "taskConstraints"
PAYLOAD_TIME_COST_PRIORITY_RATIO = "timeToCostPriorityRatio"
PAYLOAD_TIMESTAMP = "timestamp"
PAYLOAD_WORKSPACE_ID = "workspaceId"
PAYLOAD_DEBUG_MODE = "isDebugMode"
SOFTWARE_NAME = "softwareName"
SOFTWARE_VERSION = "softwareVersion"
STATUS_CODE = "statusCode"
VENDOR_NAME = "vendorName"
IS_POST_PROCESSING_INCLUDED = "isPostProcessingIncluded"
POST_PROCESSING_INFO = "postProcessingInfo"
PAYLOAD_AUTO_DELETE_DAYS = "autoDeleteDays"

# Response
BODY = "body"
GPU_RANGE = "gpuRange"
BP_HYPERTHREADING = "bpHyperthreading"
SUPPORTED_PROCESSOR_ARCHITECTURES = "supportedProcessorArchitectures"
ERROR_MESSAGE = "errorMessage"
IS_LICENSE_REQUIRED = "isLicenseRequired"
JOB_STATUS = "jobStatus"
SOFTWARE_VERSIONS = "softwareVersionCpuMap"
ERROR_MESSAGE_LIST = "errorMessageList"
