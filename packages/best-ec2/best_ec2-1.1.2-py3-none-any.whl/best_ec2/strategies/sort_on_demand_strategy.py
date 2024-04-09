import json
from typing import Dict, List, Optional, Tuple
from logging import Logger

from botocore.client import BaseClient

from ..cache import Cache
from ..constants import OS_PRODUCT_DESCRIPTION_MAP, REGIONS
from ..types import (
    FinalSpotPriceStrategy,
    InstanceTypeInfo,
    ProductDescription,
    PriceDetails,
    FilterEntry,
)
from .abstract_sort_strategy import AbstractSortStrategy


class SortOnDemandStrategy(AbstractSortStrategy):
    """Sort strategy for On-Demand EC2 instances."""

    def __init__(
        self,
        region: str,
        pricing_client: BaseClient,
        ec2_client: BaseClient,
        logger: Logger,
        concurrency_level: int,
        cache: Optional[Cache] = None,
    ):
        super().__init__(
            region,
            pricing_client,
            ec2_client,
            logger,
            concurrency_level,
            cache,
        )

    def _get_price(
        self,
        filtered_instances: List[InstanceTypeInfo],
        product_description: ProductDescription,
        availability_zones: Optional[List[str]],
        final_spot_price_strategy: FinalSpotPriceStrategy,
    ) -> Dict[str, PriceDetails]:
        operating_system = self._map_product_description_to_os(product_description)
        filters = self._build_ec2_filter_criteria(operating_system)
        return self._get_and_cache_on_demand_instance_price(filters)

    @staticmethod
    def _map_product_description_to_os(product_description: ProductDescription) -> str:
        return OS_PRODUCT_DESCRIPTION_MAP[product_description]

    def _get_on_demand_instance_price(
        self, filters: List[FilterEntry]
    ) -> Dict[str, PriceDetails]:
        paginator = self._pricing_client.get_paginator("get_products")
        records = {}

        for page in paginator.paginate(Filters=filters, ServiceCode="AmazonEC2"):
            price_list = page.get("PriceList", [])

            for price in price_list:
                instance_type, instance_price = self._parse_price_details(price)
                if instance_price > 0:
                    records[instance_type] = {"price": instance_price}

        return records

    def _build_ec2_filter_criteria(self, operating_system: str) -> List[FilterEntry]:
        return [
            {"Type": "TERM_MATCH", "Field": "preInstalledSw", "Value": "NA"},
            {
                "Type": "TERM_MATCH",
                "Field": "productFamily",
                "Value": "Compute Instance",
            },
            {"Type": "TERM_MATCH", "Field": "termType", "Value": "OnDemand"},
            {"Type": "TERM_MATCH", "Field": "location", "Value": REGIONS[self._region]},
            {
                "Type": "TERM_MATCH",
                "Field": "licenseModel",
                "Value": "No License required",
            },
            {"Type": "TERM_MATCH", "Field": "tenancy", "Value": "Shared"},
            {"Type": "TERM_MATCH", "Field": "capacitystatus", "Value": "Used"},
            {
                "Type": "TERM_MATCH",
                "Field": "operatingSystem",
                "Value": operating_system,
            },
        ]

    def _get_and_cache_on_demand_instance_price(
        self, filters: List[FilterEntry]
    ) -> Dict[str, PriceDetails]:
        cache_key = filters

        if cached_price_details := self._cache.get(cache_key):
            self._logger.info("On-demand price cache hit")
            return cached_price_details

        self._logger.info("On-demand price cache miss")
        price_details = self._get_on_demand_instance_price(filters)
        self._cache.set(cache_key, price_details)
        return price_details

    @staticmethod
    def _parse_price_details(price: str) -> Tuple[str, float]:
        details = json.loads(price)
        price_dimensions = next(iter(details["terms"]["OnDemand"].values()))[
            "priceDimensions"
        ]
        pricing_details = next(iter(price_dimensions.values()))
        instance_price = float(pricing_details["pricePerUnit"]["USD"])
        instance_type = details["product"]["attributes"]["instanceType"]

        return instance_type, instance_price
