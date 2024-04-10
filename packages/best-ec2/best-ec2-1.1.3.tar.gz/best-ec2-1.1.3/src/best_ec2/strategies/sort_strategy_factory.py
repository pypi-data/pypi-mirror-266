from ..types import UsageClass, StrategyConfig
from .abstract_sort_strategy import AbstractSortStrategy
from .sort_on_demand_strategy import SortOnDemandStrategy
from .sort_spot_strategy import SortSpotStrategy


class SortStrategyFactory:
    @staticmethod
    def create(
        usage_class: UsageClass,
        config: StrategyConfig,
    ) -> AbstractSortStrategy:
        strategy_map = {
            UsageClass.ON_DEMAND.value: SortOnDemandStrategy,
            UsageClass.SPOT.value: SortSpotStrategy,
        }

        strategy_class = strategy_map.get(usage_class)
        if strategy_class is None:
            raise ValueError(f"Unsupported usage class: {usage_class}")

        return strategy_class(config)
