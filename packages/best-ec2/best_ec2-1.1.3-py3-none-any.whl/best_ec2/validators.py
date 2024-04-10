from .types import InstanceTypeRequest, UsageClass, Architecture


class Validator:
    @staticmethod
    def instance_type_request(request: InstanceTypeRequest) -> None:
        enum_fields = {"usage_class": UsageClass, "architecture": Architecture}
        for field, enum in enum_fields.items():
            if field in request:
                valid_values = {e.value for e in enum}
                if request[field] not in valid_values:
                    raise ValueError(
                        f"Invalid {field} '{request[field]}'. Must be one of {valid_values}."
                    )

        Validator._validate_max_interruption_frequency(request)

    @staticmethod
    def _validate_max_interruption_frequency(request: InstanceTypeRequest) -> None:
        max_interruption_frequency = request.get("max_interruption_frequency")
        if max_interruption_frequency is not None and (
            not isinstance(max_interruption_frequency, int)
            or not (0 <= max_interruption_frequency <= 100)
        ):
            raise ValueError(
                f"Invalid max_interruption_frequency '{max_interruption_frequency}'. "
                "Must be an integer between 9 and 100."
            )
