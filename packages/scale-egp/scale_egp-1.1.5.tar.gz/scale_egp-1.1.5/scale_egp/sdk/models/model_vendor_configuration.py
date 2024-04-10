from enum import Enum
from typing import Dict, List, Literal, Optional, Union

from pydantic import Field

try:
    from egp_api_backend.server.api.utils.model_utils import BaseModel
except Exception:
    from pydantic import BaseModel

from .fine_tuning_jobs import TrainingDatasetORMSchemaTypeEnum
from .model_enums import ModelEndpointType, ModelVendor


class GPUType(str, Enum):
    # Supported GPU models according to
    # https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L1470-L1471
    NVIDIA_TESLA_T4 = "nvidia-tesla-t4"
    NVIDIA_AMPERE_A10 = "nvidia-ampere-a10"
    NVIDIA_AMPERE_A100 = "nvidia-ampere-a100"
    NVIDIA_AMPERE_A100e = "nvidia-ampere-a100e"


class CommonBundleConfiguration(BaseModel):
    registry: str
    image: str
    tag: str
    # Note that the command field is mandatory since we're using create_model_bundle_from_streaming_enhanced_runnable_image_v2()
    # Omitting "command" triggers this error:
    # https://github.com/scaleapi/llm-engine/blob/53a1918ef3568b674b59a4e4e772501a7e1a1d69/model-engine/model_engine_server/domain/use_cases/model_endpoint_use_cases.py#L240
    command: List[str] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)


# The fields in CreateModelBundleConfiguration(BaseModel) are based on the arguments to
# create_model_bundle_from_streaming_enhanced_runnable_image_v2() in the Launch python client:
# https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L752
# Differences between this class and the function arguments:
# * Separate fields for docker repository and image name.
# * Omitted fields: tag, healthcheck_route, predict_route, metadata - for these fields EGP user will need to
#   use the defaults provided by Launch.
#
class ModelBundleConfiguration(CommonBundleConfiguration):
    streaming_command: Optional[List[str]] = Field(None)
    readiness_initial_delay_seconds: int = Field(120)
    healthcheck_route: str = Field("/readyz")
    predict_route: str = Field("/predict")
    streaming_predict_route: Optional[str] = Field("/generate_streaming")

    @property
    def full_repository_name(self):
        return "/".join([self.registry, self.image])


# Autoscaling options which can be updated on a per-deployment basis, overriding the model configuration
# in the model template.
class LaunchAutoscalingConfiguration(BaseModel):
    # By default, we create model endpoints with min_workers = 0 so unused model endpoints can be autoscaled down to
    # 0 workers, costing nothing.
    min_workers: int = Field(0)
    max_workers: int = Field(1)
    per_worker: int = Field(
        10,
        # from: https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L1444-L1465
        description="""
The maximum number of concurrent requests that an individual worker can
service. Launch automatically scales the number of workers for the endpoint so that
each worker is processing ``per_worker`` requests, subject to the limits defined by
``min_workers`` and ``max_workers``.

- If the average number of concurrent requests per worker is lower than
``per_worker``, then the number of workers will be reduced. - Otherwise,
if the average number of concurrent requests per worker is higher than
``per_worker``, then the number of workers will be increased to meet the elevated
traffic.

Here is our recommendation for computing ``per_worker``:

1. Compute ``min_workers`` and ``max_workers`` per your minimum and maximum
throughput requirements. 2. Determine a value for the maximum number of
concurrent requests in the workload. Divide this number by ``max_workers``. Doing
this ensures that the number of workers will "climb" to ``max_workers``.
""".strip(),
    )


class RequiredResources(BaseModel):
    cpus: int = Field(3)
    memory: str = Field("8Gi")
    storage: str = Field("16Gi")
    gpus: int = Field(0)
    gpu_type: Optional[GPUType] = Field(None)


# The fields in CreateModelEndpointConfig are copied from the arguments of the Launch client's create_model_endpoint()
# https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L1391
class CreateModelEndpointConfig(LaunchAutoscalingConfiguration, RequiredResources):
    endpoint_type: ModelEndpointType = Field(ModelEndpointType.ASYNC)
    high_priority: Optional[bool] = Field(False)


class FineTuningBundleConfiguration(CommonBundleConfiguration):
    # Information for the call to create a fine tuning batch job image
    # For example, see: https://github.com/scaleapi/models/blob/19b8c83e88962ac6b6a9d52b998c35345f862e80/enterprise/egp_finetuning/docker_utils/create_docker_bundle.py#L104-L142
    # Note that some
    mount_location: Optional[str] = Field(
        default="/workspace/launch_specific/config.json",
        description="The filesystem location where the fine tuning job's configuration will be available when it is started.",
    )
    training_dataset_schema_type: Optional[TrainingDatasetORMSchemaTypeEnum] = Field(
        default=None, description="Optionally set required training and validation dataset schema"
    )
    resources: Optional[RequiredResources] = Field(default_factory=RequiredResources)


class LaunchVendorConfiguration(BaseModel):
    """
    Configuration for launching a model using the Launch service which is an internal and
    self-hosted service developed by Scale that deploys models on Kubernetes.

    Attributes:
        vendor: The vendor of the model template
        bundle_config: The bundle configuration of the model template
        endpoint_config: The endpoint configuration of the model template
    """

    # this field is required for forward compatibility (other providers will have different "vendor" fields)
    vendor: Literal[ModelVendor.LAUNCH] = Field(ModelVendor.LAUNCH)
    bundle_config: ModelBundleConfiguration
    endpoint_config: Optional[CreateModelEndpointConfig] = Field(
        default_factory=CreateModelEndpointConfig
    )
    fine_tuning_job_bundle_config: Optional[FineTuningBundleConfiguration] = Field(None)


class LaunchDeploymentVendorConfiguration(LaunchAutoscalingConfiguration):
    # this field is required for forward compatibility (other providers will have different "vendor" fields)
    vendor: Literal[ModelVendor.LAUNCH] = Field(ModelVendor.LAUNCH)


class LLMEngineDeploymentVendorConfiguration(LaunchAutoscalingConfiguration, RequiredResources):
    vendor: Literal[ModelVendor.LLMENGINE] = Field(ModelVendor.LLMENGINE)
    # The fields in the deployment configuration are the inputs to the launch client's create_llm_model_endpoint() method.
    # https://github.com/scaleapi/launch-python-client/blob/794089b9ed58330a7ecac02eb5060bcc4ae3d409/launch/client.py#L2603
    # The fields in LaunchAutoscalingConfiguration (min_workers, max_workers, per_worker)
    # and RequiredResources (cpus, memory, storage, gpus, gpu_type)
    # are inherited. All other applicable parameters of create_llm_model_endpoint() are represented as fields of this class.
    # QUESTION: endpoint_type must be "async" for vLLM, right?
    high_priority: bool = Field(False)
    # QUESTION: We can get away with requiring SGP users to use the latest tag, right?
    # If so, we don't need to expose inference_framework_image_tag
    # QUESTION: It seems like source is always "hugging_face", can we leave it out?
    # QUESTION: Only vLLM will be supported, right? If so, we won't need inference_framework
    num_shards: int = Field(default=4)
    # QUESTION: Is the value of quantize always "bitsandbytes"? If so we can leave it out.
    # TODO: this should probably be a full URI not just a path in S3 relative to a specific bucket
    # since single-tenant EGP instance will have their own buckets, azure instances won't use S3, etc,
    # but I don't want to deviate from create_llm_model_endpoint() parameter names and using a full URL
    # would also require support from model-engine.
    checkpoint_path: Optional[str] = Field(None)


ModelVendorConfiguration = LaunchVendorConfiguration


class DeploymentVendorConfiguration(BaseModel):
    __root__: Union[LaunchDeploymentVendorConfiguration, LLMEngineDeploymentVendorConfiguration] = (
        Field(..., discriminator="vendor")
    )
