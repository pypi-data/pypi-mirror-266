from typing import List, Union

from botocore.client import BaseClient

from .exceptions import NoAvailabilityZonesError


class AwsUtils:
    def __init__(self, ec2_client: BaseClient):
        self._availability_zones_cache: Union[None, List[str]] = None
        self._ec2_client = ec2_client

    def get_region(self) -> str:
        return self._ec2_client.meta.region_name

    def get_all_availability_zones_for_region(self) -> List[str]:
        if self._availability_zones_cache is None:
            self._fetch_and_cache_availability_zones()

        return self._availability_zones_cache

    def _fetch_and_cache_availability_zones(self):
        response = self._ec2_client.describe_availability_zones()
        if availability_zones := [
            zone["ZoneName"] for zone in response.get("AvailabilityZones", [])
        ]:
            self._availability_zones_cache = availability_zones
        else:
            raise NoAvailabilityZonesError(self.get_region())
