from abc import ABC, abstractmethod
from typing import List
import copy

from .constants import OS_PRODUCT_DESCRIPTION_MAP
from .spot_utils import SpotUtils
from .types import InstanceTypeInfo, InstanceTypeRequest, UsageClass


class Filter(ABC):
    @abstractmethod
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        pass


class VcpuFilter(Filter):
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        return [
            i
            for i in instances
            if i["VCpuInfo"]["DefaultVCpus"] >= request.get("vcpu", 0)
        ]


class MemoryFilter(Filter):
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        return [
            i
            for i in instances
            if i["MemoryInfo"]["SizeInMiB"] >= request.get("memory_gb", 0) * 1024
        ]


class UsageClassFilter(Filter):
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        usage_class = request.get("usage_class")
        if usage_class is None:
            return instances
        return [i for i in instances if usage_class in i["SupportedUsageClasses"]]


class BurstableFilter(Filter):
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        burstable = request.get("burstable")
        return (
            [i for i in instances if i["BurstablePerformanceSupported"] == burstable]
            if burstable is not None
            else instances
        )


class ArchitectureFilter(Filter):
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        architecture = request.get("architecture")
        return (
            [
                i
                for i in instances
                if architecture in i["ProcessorInfo"]["SupportedArchitectures"]
            ]
            if architecture is not None
            else instances
        )


class GpuFilter(Filter):
    def _filter_instances_with_gpu(
        self, instances: List[InstanceTypeInfo], gpu_memory: int, gpus: int
    ) -> List[InstanceTypeInfo]:
        """Filter instances that meet the GPU requirements."""
        return [
            instance
            for instance in instances
            if "GpuInfo" in instance
            and instance["GpuInfo"]["TotalGpuMemoryInMiB"] >= gpu_memory * 1024
            and sum(gpu["Count"] for gpu in instance["GpuInfo"]["Gpus"]) >= gpus
        ]

    def _filter_instances_without_gpu(
        self, instances: List[InstanceTypeInfo]
    ) -> List[InstanceTypeInfo]:
        return [instance for instance in instances if "GpuInfo" not in instance]

    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        has_gpu = request.get("has_gpu")

        if has_gpu is None:
            return instances

        if has_gpu:
            gpu_memory = request.get("gpu_memory", 0)
            gpus = request.get("gpus", 0)
            return self._filter_instances_with_gpu(instances, gpu_memory, gpus)

        return self._filter_instances_without_gpu(instances)


class SpotFilter(Filter):
    def __init__(self, region: str):
        self._region = region

    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        if (
            request.get("usage_class") != UsageClass.SPOT.value
            or "max_interruption_frequency" not in request
        ):
            return instances

        spot_utils = SpotUtils(self._region)
        operating_system = OS_PRODUCT_DESCRIPTION_MAP.get(
            request["product_description"]
        )
        interruption_frequencies = spot_utils.get_spot_interruption_frequency(
            operating_system
        )

        """
        Copy instances to ensure immutability: This is crucial as instances stored in cache are shared across 
        different usage classes (spot and on-demand).
        """
        copied_instances = list(map(copy.copy, instances))

        for instance in copied_instances:
            instance_type = instance["InstanceType"]
            instance["InterruptionFrequency"] = interruption_frequencies.get(
                instance_type
            )

        max_freq = request["max_interruption_frequency"]

        return [
            instance
            for instance in copied_instances
            if instance["InterruptionFrequency"]
            and instance["InterruptionFrequency"]["min"] <= max_freq
        ]


class CurrentGenerationFilter(Filter):
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        is_current_generation = request.get("is_current_generation")
        if is_current_generation is not None:
            return [
                i for i in instances if i["CurrentGeneration"] == is_current_generation
            ]

        return instances


class InstanceStorageSupportedFilter(Filter):
    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        is_instance_storage_supported = request.get("is_instance_storage_supported")
        if is_instance_storage_supported is not None:
            return [
                i
                for i in instances
                if i["InstanceStorageSupported"] == is_instance_storage_supported
            ]

        return instances


class FilterChain:
    def __init__(self, region: str):
        self._filters: List[Filter] = [
            VcpuFilter(),
            MemoryFilter(),
            UsageClassFilter(),
            BurstableFilter(),
            ArchitectureFilter(),
            GpuFilter(),
            SpotFilter(region),
            CurrentGenerationFilter(),
            InstanceStorageSupportedFilter(),
        ]

    def execute(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        for filter_ in self._filters:
            instances = filter_.apply(instances, request)
        return instances
