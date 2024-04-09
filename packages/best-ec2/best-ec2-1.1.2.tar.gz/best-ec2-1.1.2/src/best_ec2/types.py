from datetime import datetime
from enum import Enum
from typing import Optional, Dict, TypeVar, TypedDict, List, Union

from botocore.client import BaseClient
from botocore.config import Config


class UsageClass(Enum):
    SPOT = "spot"
    ON_DEMAND = "on-demand"


class Architecture(Enum):
    I386 = "i386"
    X86_64 = "x86_64"
    ARM64 = "arm64"
    X86_64_MAC = "x86_64_mac"


class ProductDescription(Enum):
    LINUX_UNIX = "Linux/UNIX"
    RED_HAT_ENTERPRISE_LINUX = "Red Hat Enterprise Linux"
    SUSE_LINUX = "SUSE Linux"
    WINDOWS = "Windows"
    LINUX_UNIX_VPC = "Linux/UNIX (Amazon VPC)"
    RED_HAT_ENTERPRISE_LINUX_VPC = "Red Hat Enterprise Linux (Amazon VPC)"
    SUSE_LINUX_VPC = "SUSE Linux (Amazon VPC)"
    WINDOWS_VPC = "Windows (Amazon VPC)"


class FinalSpotPriceStrategy(Enum):
    MIN = "min"
    MAX = "max"
    AVERAGE = "average"


class InterruptionFrequencyInfo(TypedDict):
    min: int
    max: int
    rate: str


class DiskInfo(TypedDict):
    SizeInGB: int
    Count: int
    Type: str


class InstanceStorageInfo(TypedDict):
    Disks: List[DiskInfo]


class GpuInfo(TypedDict):
    total_gpu_memory: int


class _InstanceTypeRequired(TypedDict):
    price: float
    instance_type: str
    vcpu: int
    memory_gb: int
    network_performance: str
    storage: Union[str, List[DiskInfo]]


class InstanceType(_InstanceTypeRequired, total=False):
    az_price: Optional[Dict[str, float]]
    interruption_frequency: Optional[InterruptionFrequencyInfo]
    gpu_memory_gb: Optional[int]
    gpus: Optional[int]


InstanceTypeResponse = List[InstanceType]


class ClientsDict(TypedDict, total=False):
    ec2: Optional[BaseClient]
    pricing: Optional[BaseClient]


class BestEc2Options(TypedDict, total=False):
    describe_spot_price_history_concurrency: Optional[int]
    describe_on_demand_price_concurrency: Optional[int]
    result_cache_ttl_in_minutes: Optional[int]
    instance_type_cache_ttl_in_minutes: Optional[int]
    on_demand_price_cache_ttl_in_minutes: Optional[int]
    spot_price_cache_ttl_in_minutes: Optional[int]
    log_level: Optional[int]


class NetworkInfo(TypedDict):
    NetworkPerformance: str


class VCpuInfo(TypedDict):
    DefaultVCpus: int


class InstanceTypeInfo(TypedDict):
    InstanceType: str
    CurrentGeneration: bool
    FreeTierEligible: bool
    SupportedUsageClasses: List[str]
    SupportedRootDeviceTypes: List[str]
    SupportedVirtualizationTypes: List[str]
    BareMetal: bool
    Hypervisor: str
    ProcessorInfo: Dict[str, Union[List[str], float, List[str]]]
    VCpuInfo: VCpuInfo
    MemoryInfo: Dict[str, int]
    InstanceStorageSupported: bool
    InstanceStorageInfo: Optional[InstanceStorageInfo]
    EbsInfo: Dict[str, Union[str, Dict[str, Union[int, float]]]]
    NetworkInfo: NetworkInfo
    PlacementGroupInfo: Dict[str, List[str]]
    HibernationSupported: bool
    BurstablePerformanceSupported: bool
    DedicatedHostsSupported: bool
    AutoRecoverySupported: bool
    SupportedBootModes: List[str]
    NitroEnclavesSupport: str
    NitroTpmSupport: str
    NitroTpmInfo: Dict[str, List[str]]
    InterruptionFrequency: Optional[InterruptionFrequencyInfo]
    GpuInfo: Optional[GpuInfo]


class InstanceTypeRequest(TypedDict, total=False):
    vcpu: Optional[float]
    memory_gb: Optional[float]
    region: Optional[str]
    usage_class: Optional[UsageClass]
    burstable: Optional[bool]
    architecture: Optional[Architecture]
    product_description: Optional[ProductDescription]
    is_current_generation: Optional[bool]
    has_gpu: Optional[bool]
    gpu_memory: Optional[int]
    gpus: Optional[int]
    is_instance_storage_supported: Optional[bool]
    max_interruption_frequency: Optional[int]
    availability_zones: Optional[List[str]]
    final_spot_price_strategy: Optional[FinalSpotPriceStrategy]
    ec2_client_config: Optional[Config]


class RequestConfig(TypedDict, total=False):
    ec2_client_config: Optional[Config]


V = TypeVar("V")


class CacheEntry(TypedDict):
    result: V
    datetime: datetime


CacheDict = Dict[str, CacheEntry]


class DescribeInstanceTypeRequest(TypedDict, total=False):
    is_current_generation: Optional[bool]
    is_instance_storage_supported: Optional[bool]


class _PriceDetails(TypedDict):
    price: float


class PriceDetails(_PriceDetails, total=False):
    az_price: Optional[Dict[str, float]]


class TypePriceDetails(TypedDict):
    instance_type: str
    price_details: PriceDetails


class FilterEntry(TypedDict):
    Type: str
    Field: str
    Value: str


class SpotPriceCacheKey(TypedDict):
    filtered_instances: List[InstanceTypeInfo]
    product_description: ProductDescription
    availability_zones: Optional[List[str]]
    final_spot_price_strategy: FinalSpotPriceStrategy
