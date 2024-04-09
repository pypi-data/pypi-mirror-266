from logging import Logger
from botocore.client import BaseClient
from ..types import UsageClass
from .abstract_sort_strategy import AbstractSortStrategy
from .sort_on_demand_strategy import SortOnDemandStrategy
from .sort_spot_strategy import SortSpotStrategy
from ..cache import Cache


class SortStrategyFactory:
    @staticmethod
    def create(
        usage_class: UsageClass,
        region: str,
        pricing_client: BaseClient,
        ec2_client: BaseClient,
        logger: Logger,
        concurrency: int,
        cache: Cache,
    ) -> AbstractSortStrategy:
        strategy_map = {
            UsageClass.ON_DEMAND.value: SortOnDemandStrategy,
            UsageClass.SPOT.value: SortSpotStrategy,
        }

        strategy_class = strategy_map.get(usage_class)
        if strategy_class is None:
            raise ValueError(f"Unsupported usage class: {usage_class}")

        return strategy_class(
            region, pricing_client, ec2_client, logger, concurrency, cache
        )
