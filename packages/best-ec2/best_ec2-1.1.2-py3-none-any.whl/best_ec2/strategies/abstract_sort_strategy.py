from abc import ABC, abstractmethod
import operator
from logging import Logger
from typing import Dict, List, Optional, Union

from botocore.client import BaseClient

from ..types import (
    FinalSpotPriceStrategy,
    InstanceTypeInfo,
    InstanceTypeResponse,
    ProductDescription,
    InstanceType,
    PriceDetails,
)
from ..cache import Cache


class AbstractSortStrategy(ABC):
    def __init__(
        self,
        region: str,
        pricing_client: BaseClient,
        ec2_client: BaseClient,
        logger: Logger,
        concurrency_level: int,
        cache: Cache,
    ):
        self._logger = logger
        self._region = region
        self._pricing_client = pricing_client
        self._ec2_client = ec2_client
        self._concurrency_level = concurrency_level
        self._cache = cache

    def sort(
        self,
        instance_types_info: List[InstanceTypeInfo],
        product_desc: ProductDescription,
        availability_zones: List[str],
        pricing_strategy: Optional[FinalSpotPriceStrategy],
    ) -> InstanceTypeResponse:
        price_details_by_instance = self._get_price(
            instance_types_info,
            product_desc,
            availability_zones,
            pricing_strategy,
        )

        sorted_instances = []
        for instance_info in instance_types_info:
            instance_entry = self._build_instance_entry(
                instance_info, price_details_by_instance
            )
            if instance_entry is not None:
                sorted_instances.append(instance_entry)

        sorted_instances.sort(key=operator.itemgetter("price"))

        return sorted_instances

    @abstractmethod
    def _get_price(
        self,
        filtered_instances: List[InstanceTypeInfo],
        product_description: ProductDescription,
        availability_zones: Optional[List[str]],
        final_spot_price_strategy: FinalSpotPriceStrategy,
    ) -> Dict[str, PriceDetails]:
        pass

    def _build_instance_entry(
        self,
        instance_info: InstanceTypeInfo,
        prices: Dict[str, PriceDetails],
    ) -> Union[InstanceType, None]:
        instance_type_name = instance_info["InstanceType"]
        price_info = prices.get(instance_type_name)

        if price_info is None:
            self._logger.debug(
                f"The price for the {instance_type_name} instance type not found"
            )
            return None

        entry: InstanceType = {
            "instance_type": instance_type_name,
            "vcpu": instance_info["VCpuInfo"]["DefaultVCpus"],
            "memory_gb": self._transform_memory_size(
                instance_info["MemoryInfo"]["SizeInMiB"]
            ),
            "network_performance": instance_info["NetworkInfo"]["NetworkPerformance"],
            "storage": instance_info.get("InstanceStorageInfo", {}).get(
                "Disks", "EBS Only"
            ),
            "price": price_info["price"],
        }

        if az_price := price_info.get("az_price"):
            entry["az_price"] = az_price

        if gpu_info := instance_info.get("GpuInfo"):
            entry["gpu_memory_gb"] = self._transform_memory_size(
                gpu_info["TotalGpuMemoryInMiB"]
            )
            entry["gpus"] = sum(gpu["Count"] for gpu in gpu_info["Gpus"])

        if interruption_frequency := instance_info.get("InterruptionFrequency"):
            entry["interruption_frequency"] = interruption_frequency

        return entry

    @staticmethod
    def _transform_memory_size(memory_in_mib: int) -> int:
        """Converts memory size from MiB to GB"""
        return memory_in_mib // 1024
