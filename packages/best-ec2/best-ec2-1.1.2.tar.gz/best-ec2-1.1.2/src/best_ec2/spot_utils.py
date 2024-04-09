import json
from urllib import request

from .constants import SPOT_ADVISOR_JSON_URL


class SpotUtils:
    def __init__(self, region):
        self.__region = region

    def get_spot_interruption_frequency(self, os):
        results = {}
        with request.urlopen(SPOT_ADVISOR_JSON_URL) as response:
            response_data = response.read().decode("utf-8")
            spot_advisor = json.loads(response_data)["spot_advisor"]

        rates = {
            0: {"min": 0, "max": 5, "rate": "<5%"},
            1: {"min": 6, "max": 10, "rate": "5-10%"},
            2: {"min": 11, "max": 15, "rate": "10-15%"},
            3: {"min": 16, "max": 20, "rate": "15-20%"},
            4: {"min": 21, "max": 100, "rate": ">20%"},
        }

        instance_data = spot_advisor[self.__region].get(os, {})

        for instance_type, data in instance_data.items():
            rate = data["r"]
            results[instance_type] = rates[rate]

        return results
