from functools import reduce
from abc import ABC, abstractmethod
from typing import List
import copy

from .constants import OS_PRODUCT_DESCRIPTION_MAP
from .spot_utils import SpotUtils
from .types import InstanceTypeInfo, InstanceTypeRequest, UsageClass


class Enricher(ABC):
    """
    Interface for instance enrichment.
    """

    @abstractmethod
    def apply(
        self, instances: list[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> list[InstanceTypeInfo]:
        """
        Enrich the instance data based on the request.
        """
        raise NotImplementedError("Method 'apply' must be implemented in a subclass")


class SpotEnricher(Enricher):
    def __init__(self, region: str):
        self._region = region
        self.spot_utils = SpotUtils(self._region)

    def apply(
        self, instances: list[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> list[InstanceTypeInfo]:
        if request.get("usage_class") != UsageClass.SPOT.value:
            return instances

        spot_utils = SpotUtils(self._region)
        operating_system = OS_PRODUCT_DESCRIPTION_MAP.get(
            request["product_description"]
        )
        interruption_frequencies = spot_utils.get_spot_interruption_frequency(
            operating_system
        )

        # Copy instances to ensure immutability: This is crucial as instances stored in cache are shared
        # across different usage classes (spot and on-demand).
        copied_instances = list(map(copy.copy, instances))

        for instance in copied_instances:
            instance["InterruptionFrequency"] = interruption_frequencies.get(
                instance["InstanceType"]
            )

        return copied_instances


class EnricherChain:
    def __init__(self, region: str):
        self._filters: List[Enricher] = [SpotEnricher(region)]

    def apply(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        return reduce(
            lambda acc, filter_: filter_.apply(acc, request),
            self._filters,
            instances,
        )
