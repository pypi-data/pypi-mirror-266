class NoAvailabilityZonesError(Exception):
    """Exception raised when no availability zones are found for a given AWS region."""

    def __init__(
        self, region, message="Availability zones not found for the specified region"
    ):
        self.region = region
        self.message = f"{message}: {region}"
        super().__init__(self.message)


class InvalidStrategyError(ValueError):
    """Exception raised when an invalid strategy is provided."""

    def __init__(self, strategy, message="The specified strategy is invalid"):
        self.strategy = strategy
        self.message = f"{message}: {strategy}"
        super().__init__(self.message)
