import logging
from logging import Logger
from typing import Optional, List, Dict
import time
from contextlib import contextmanager

import boto3
from botocore.config import Config
from botocore.client import BaseClient

from .types import (
    BestEc2Options,
    InstanceTypeRequest,
    InstanceTypeResponse,
    ProductDescription,
    UsageClass,
    Architecture,
    InstanceTypeInfo,
    FilterEntry,
    PriceDetails,
    SpotPriceCacheKey,
    RequestConfig,
)
from .constants import (
    DEFAULT_RESULT_CACHE_TTL_IN_MINUTES,
    DEFAULT_INSTANCE_TYPE_CACHE_TTL_IN_MINUTES,
    DEFAULT_ON_DEMAND_PRICE_CACHE_TTL_IN_MINUTES,
    DEFAULT_SPOT_PRICE_CACHE_TTL_IN_MINUTES,
    DEFAULT_SPOT_CONCURRENCY,
    DEFAULT_REGION,
    DEFAULT_VCPU,
    DEFAULT_MEMORY_GB,
)
from .strategies.sort_strategy_factory import SortStrategyFactory
from .cache import Cache
from .validators import Validator
from .filters import FilterChain
from .utils import remove_none_values


class BestEc2Impl:
    def __init__(
        self, options: Optional[BestEc2Options] = None, logger: Optional[Logger] = None
    ):
        options = options if options is not None else {}
        result_cache_ttl_in_minutes = options.get(
            "result_cache_ttl_in_minutes", DEFAULT_RESULT_CACHE_TTL_IN_MINUTES
        )
        instance_type_cache_ttl_in_minutes = options.get(
            "instance_type_cache_ttl_in_minutes",
            DEFAULT_INSTANCE_TYPE_CACHE_TTL_IN_MINUTES,
        )
        on_demand_price_cache_ttl_in_minutes = options.get(
            "on_demand_price_cache_ttl_in_minutes",
            DEFAULT_ON_DEMAND_PRICE_CACHE_TTL_IN_MINUTES,
        )
        spot_price_cache_ttl_in_minutes = options.get(
            "spot_price_cache_ttl_in_minutes", DEFAULT_SPOT_PRICE_CACHE_TTL_IN_MINUTES
        )
        self._result_cache = Cache[InstanceTypeRequest, InstanceTypeResponse](
            result_cache_ttl_in_minutes
        )
        self._logger = logger or self._setup_default_logger(
            options.get("log_level", logging.INFO)
        )
        self._spot_price_history_concurrency = options.get(
            "describe_spot_price_history_concurrency", DEFAULT_SPOT_CONCURRENCY
        )
        self._instance_type_cache = Cache[str, List[InstanceTypeInfo]](
            instance_type_cache_ttl_in_minutes
        )
        self._on_demand_price_cache = Cache[List[FilterEntry], Dict[str, PriceDetails]](
            on_demand_price_cache_ttl_in_minutes
        )
        self._spot_price_cache = Cache[SpotPriceCacheKey, Dict[str, PriceDetails]](
            spot_price_cache_ttl_in_minutes
        )

    @staticmethod
    def _setup_default_logger(log_level: int) -> logging.Logger:
        logger = logging.getLogger()
        logger.setLevel(log_level)
        formatter = logging.Formatter(
            "%(asctime)s - %(threadName)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        return logger

    def get_types(
        self,
        request: Optional[InstanceTypeRequest] = None,
        config: Optional[RequestConfig] = None,
    ) -> InstanceTypeResponse:
        request = self._prepare_request_with_defaults(remove_none_values(request))
        ec2_client = self._create_ec2_client(request, config)

        Validator.instance_type_request(request)

        cached_result = self._check_cache(request)
        if cached_result:
            return cached_result

        with self._log_runtime("get types"):
            instances = self._describe_and_cache_instance_types(
                ec2_client, request["region"]
            )
        filtered_instances = self._apply_filters_to_instances(instances, request)

        with self._log_runtime("get price"):
            sorted_instances = self._sort_instances_by_strategy(
                filtered_instances, request, ec2_client
            )

        self._cache_result(request, sorted_instances)
        return sorted_instances

    def _create_ec2_client(
        self,
        request: InstanceTypeRequest,
        request_config: Optional[RequestConfig] = None,
    ) -> BaseClient:
        config = (
            request_config["ec2_client_config"]
            if request_config and "ec2_client_config" in request_config
            else Config(max_pool_connections=self._spot_price_history_concurrency)
        )

        try:
            return boto3.client("ec2", region_name=request["region"], config=config)
        except boto3.exceptions.Boto3Error as e:
            self._logger.error(f"Error creating EC2 client: {e}")
            raise

    def _check_cache(self, request):
        cached_result = self._result_cache.get(request)
        if cached_result:
            self._logger.info("Result cache hit")
        else:
            self._logger.info("Result cache miss")
        return cached_result

    @contextmanager
    def _log_runtime(self, operation_name: str):
        start_time = time.time()
        yield
        end_time = time.time()
        runtime = end_time - start_time
        self._logger.info(f"Runtime for {operation_name}: {runtime} seconds")

    @staticmethod
    def _prepare_request_with_defaults(
        request: Optional[InstanceTypeRequest],
    ) -> InstanceTypeRequest:
        if request is None:
            request = {}
        request.setdefault("vcpu", DEFAULT_VCPU)
        request.setdefault("memory_gb", DEFAULT_MEMORY_GB)
        request.setdefault("region", DEFAULT_REGION)
        request.setdefault("usage_class", UsageClass.ON_DEMAND.value)
        request.setdefault("architecture", Architecture.X86_64.value)
        request.setdefault("product_description", ProductDescription.LINUX_UNIX.value)
        return request

    def _apply_filters_to_instances(
        self, instances: List[InstanceTypeInfo], request: InstanceTypeRequest
    ) -> List[InstanceTypeInfo]:
        self._logger.debug(
            f"Number of instance types before filtering: {len(instances)}"
        )
        filtered_instances = FilterChain(request.get("region")).execute(
            instances, request
        )
        self._logger.debug(
            f"Number of instance types after filtering: {len(filtered_instances)}"
        )
        return filtered_instances

    def _sort_instances_by_strategy(
        self,
        instances: List[InstanceTypeInfo],
        request: InstanceTypeRequest,
        ec2_client: BaseClient,
    ) -> InstanceTypeResponse:
        config = Config(max_pool_connections=self._spot_price_history_concurrency)
        # Use the us-east-1 region for the AWS Pricing API as it is the only supported region for this service
        pricing_client = boto3.client("pricing", region_name="us-east-1", config=config)
        strategy = SortStrategyFactory.create(
            request["usage_class"],
            request.get("region"),
            pricing_client,
            ec2_client,
            self._logger,
            self._spot_price_history_concurrency,
            self._on_demand_price_cache
            if request["usage_class"] == UsageClass.ON_DEMAND.value
            else self._spot_price_cache,
        )
        return strategy.sort(
            instances,
            request["product_description"],
            request.get("availability_zones"),
            request.get("final_spot_price_strategy", "min"),
        )

    def _cache_result(
        self, request: InstanceTypeRequest, result: InstanceTypeResponse
    ) -> None:
        self._result_cache.set(request, result)

    def _describe_instance_types(
        self, ec2_client: BaseClient
    ) -> List[InstanceTypeInfo]:
        instances = []
        paginator = ec2_client.get_paginator("describe_instance_types")
        for page in paginator.paginate():
            instances.extend(page["InstanceTypes"])

        return instances

    def _describe_and_cache_instance_types(
        self, ec2_client: BaseClient, region: str
    ) -> List[InstanceTypeInfo]:
        if cached_result := self._instance_type_cache.get(region):
            self._logger.info("Instance type cache hit")
            return cached_result
        self._logger.info("Instance type cache miss")
        instances = self._describe_instance_types(ec2_client)
        self._instance_type_cache.set(region, instances)
        return instances
