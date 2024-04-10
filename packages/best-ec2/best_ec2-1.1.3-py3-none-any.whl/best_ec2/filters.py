from abc import ABC, abstractmethod
from typing import List

from .types import InstanceTypeInfo, InstanceTypeRequest, UsageClass
from .constants import MEBIBYTES_IN_GIBIBYTE


class Filter(ABC):
    @abstractmethod
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        pass


class VcpuFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        return instance["VCpuInfo"]["DefaultVCpus"] >= request.get("vcpu", 0)


class MemoryFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        return (
            instance["MemoryInfo"]["SizeInMiB"]
            >= request.get("memory_gb", 0) * MEBIBYTES_IN_GIBIBYTE
        )


class UsageClassFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        usage_class = request.get("usage_class")

        if not instance["SupportedUsageClasses"]:
            raise ValueError("SupportedUsageClasses is empty")

        return usage_class in instance["SupportedUsageClasses"]


class BurstableFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        burstable = request.get("burstable")
        if burstable is None:
            return True
        return instance["BurstablePerformanceSupported"] == burstable


class ArchitectureFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        architecture = request.get("architecture")

        if not instance["ProcessorInfo"]["SupportedArchitectures"]:
            raise ValueError("SupportedUsageClasses is empty")

        return (
            architecture is None
            or architecture in instance["ProcessorInfo"]["SupportedArchitectures"]
        )


class GpuFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        has_gpu = request.get("has_gpu")
        gpu_memory = request.get("gpu_memory", 0) * MEBIBYTES_IN_GIBIBYTE
        gpus = request.get("gpus", 0)

        if has_gpu is None:
            return True
        if has_gpu and "GpuInfo" in instance:
            is_memory_sufficient = (
                instance["GpuInfo"]["TotalGpuMemoryInMiB"] >= gpu_memory
            )
            are_gpus_sufficient = (
                sum(gpu["Count"] for gpu in instance["GpuInfo"]["Gpus"]) >= gpus
            )
            return is_memory_sufficient and are_gpus_sufficient
        return not has_gpu and "GpuInfo" not in instance


class SpotFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        if request.get("usage_class") != UsageClass.SPOT.value:
            return True
        if instance["InterruptionFrequency"] is None:
            return False
        max_freq = request.get("max_interruption_frequency")
        if max_freq is None:
            return True
        return instance["InterruptionFrequency"]["min"] <= max_freq


class CurrentGenerationFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        is_current_generation = request.get("is_current_generation")
        return (
            is_current_generation is None
            or instance["CurrentGeneration"] == is_current_generation
        )


class InstanceStorageSupportedFilter(Filter):
    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        is_instance_storage_supported = request.get("is_instance_storage_supported")
        return (
            is_instance_storage_supported is None
            or instance["InstanceStorageSupported"] == is_instance_storage_supported
        )


class FilterChain:
    def __init__(self):
        self._filters: List[Filter] = [
            VcpuFilter(),
            MemoryFilter(),
            UsageClassFilter(),
            BurstableFilter(),
            ArchitectureFilter(),
            GpuFilter(),
            SpotFilter(),
            CurrentGenerationFilter(),
            InstanceStorageSupportedFilter(),
        ]

    def apply(self, instance: InstanceTypeInfo, request: InstanceTypeRequest) -> bool:
        return all(filter_.apply(instance, request) for filter_ in self._filters)
