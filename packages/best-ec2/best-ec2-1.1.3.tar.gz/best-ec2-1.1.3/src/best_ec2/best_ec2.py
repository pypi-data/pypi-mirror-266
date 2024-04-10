from typing import Optional
from logging import Logger

from .types import (
    BestEc2Options,
    InstanceTypeRequest,
    InstanceTypeResponse,
    RequestConfig,
)
from .best_ec2_impl import BestEc2Impl


class BestEc2:
    def __init__(
        self, options: Optional[BestEc2Options] = None, logger: Optional[Logger] = None
    ):
        self.__impl: BestEc2Impl = BestEc2Impl(options, logger)

    def get_types(
        self,
        request: Optional[InstanceTypeRequest] = None,
        config: Optional[RequestConfig] = None,
    ) -> InstanceTypeResponse:
        return self.__impl.get_types(request, config)
