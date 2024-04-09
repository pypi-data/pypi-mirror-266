from logging import Logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from botocore.client import BaseClient

from ..types import (
    FinalSpotPriceStrategy,
    InstanceTypeInfo,
    ProductDescription,
    PriceDetails,
    TypePriceDetails,
)
from ..aws_utils import AwsUtils
from ..exceptions import InvalidStrategyError
from ..cache import Cache
from .abstract_sort_strategy import AbstractSortStrategy


class SortSpotStrategy(AbstractSortStrategy):
    def __init__(
        self,
        region: str,
        pricing_client: BaseClient,
        ec2_client: BaseClient,
        logger: Logger,
        spot_price_history_concurrency: int,
        cache: Cache,
    ):
        super().__init__(
            region,
            pricing_client,
            ec2_client,
            logger,
            spot_price_history_concurrency,
            cache,
        )
        self._aws_utils = AwsUtils(ec2_client)

    def _get_price(
        self,
        filtered_instances: List[InstanceTypeInfo],
        product_description: ProductDescription,
        availability_zones: Optional[List[str]],
        final_spot_price_strategy: FinalSpotPriceStrategy,
    ) -> Dict[str, PriceDetails]:
        availability_zones = (
            availability_zones
            or self._aws_utils.get_all_availability_zones_for_region()
        )

        cache_key = {
            "filtered_instances": filtered_instances,
            "product_description": product_description,
            "availability_zones": availability_zones,
            "final_spot_price_strategy": final_spot_price_strategy,
        }

        if cached_price_details := self._cache.get(cache_key):
            self._logger.info("Spot price cache hit")
            return cached_price_details
        self._logger.info("Spot price cache miss")

        with ThreadPoolExecutor(max_workers=self._concurrency_level) as executor:
            futures = [
                executor.submit(
                    self._get_spot_instance_price,
                    ec2_instance,
                    product_description,
                    availability_zones,
                    final_spot_price_strategy,
                )
                for ec2_instance in filtered_instances
            ]

            ec2_prices = {
                future.result()["instance_type"]: future.result()["price_details"]
                for future in as_completed(futures)
                if future.result()
            }

        self._cache.set(cache_key, ec2_prices)
        return ec2_prices

    def _get_spot_instance_price(
        self,
        ec2_instance: InstanceTypeInfo,
        product_description: ProductDescription,
        availability_zones: List[str],
        strategy: FinalSpotPriceStrategy,
    ) -> Optional[TypePriceDetails]:
        instance_type = ec2_instance["InstanceType"]
        filters = [{"Name": "product-description", "Values": [product_description]}]

        if availability_zones:
            filters.append({"Name": "availability-zone", "Values": availability_zones})

        response = self._ec2_client.describe_spot_price_history(
            InstanceTypes=[instance_type], Filters=filters
        )

        history_events = response["SpotPriceHistory"]
        az_price: Dict[str, float] = {
            event["AvailabilityZone"]: float(event["SpotPrice"])
            for event in history_events
            if event["AvailabilityZone"] in availability_zones
        }

        prices = list(az_price.values())

        if len(prices) == 0:
            self._logger.info(f"Spot price for the {instance_type} is not available")
            return None

        spot_price = self._calculate_spot_price(prices, strategy)

        return {
            "instance_type": instance_type,
            "price_details": {"price": spot_price, "az_price": az_price},
        }

    @staticmethod
    def _calculate_spot_price(
        prices: List[float], strategy: FinalSpotPriceStrategy
    ) -> float:
        if strategy == "average":
            return sum(prices) / len(prices)
        elif strategy == "max":
            return max(prices)
        elif strategy == "min":
            return min(prices)
        else:
            raise InvalidStrategyError(strategy)
