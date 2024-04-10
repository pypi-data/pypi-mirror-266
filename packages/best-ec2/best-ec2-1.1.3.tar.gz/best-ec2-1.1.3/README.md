# Best EC2

Best EC2, the smart solution designed to optimize your Amazon EC2 instance type selection process. The app simplifies the challenge of choosing the optimal EC2 instance type that matches your specific requirements, balancing performance, cost, and computing needs.

# Prerequisites
* python >=3.8.0
* AWS Credentials

# Install
pip install best-ec2

# The IAM policy grants minimal permissions necessary for the application

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "General",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstanceTypes"
            ],
            "Resource": "*"
        },
        {
            "Sid": "OnDemand",
            "Effect": "Allow",
            "Action": [
                "pricing:GetProducts"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Spot",
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeAvailabilityZones",
                "ec2:DescribeSpotPriceHistory"
            ],
            "Resource": "*"
        }
    ]
}
```

# BestEc2Options

| Parameter                                 | Type            | Description                                      | Required | Default | Possible Values                                |
|-------------------------------------------|-----------------|--------------------------------------------------|----------|---------|------------------------------------------------|
| `describe_spot_price_history_concurrency` | `Optional[int]` | Concurrency level for retrieving spot prices     | No       | 20      | -                                              |
| `describe_on_demand_price_concurrency`    | `Optional[int]` | Concurrency level for retrieving on-demand prices| No       | 10      | -                                              |
| `result_cache_ttl_in_minutes`             | `Optional[int]` | Time-to-live for cached results                  | No       | 60      | -                                              |
| `instance_type_cache_ttl_in_minutes`      | `Optional[int]` | Time-to-live for cached instance type list       | No       | 1440    | -                                              |
| `on_demand_price_cache_ttl_in_minutes`    | `Optional[int]` | Time-to-live for cached on-demand prices         | No       | 1440    | -                                              |
| `spot_price_cache_ttl_in_minutes`         | `Optional[int]` | Time-to-live for cached spot prices              | No       | 10      | -                                              |
| `log_level`                               | `Optional[int]` | Log level                                        | No       | `INFO` (20) | CRITICAL (50), ERROR (40), WARNING (30), INFO (20), DEBUG (10), NOTSET (0) |

# InstanceTypeRequest

| Parameter                       | Type                         | Description                                                                                                                       | Required | Default      | Values                                                                                                                                        |
|---------------------------------|------------------------------|-----------------------------------------------------------------------------------------------------------------------------------|----------|--------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `vcpu`                          | `Optional[float]`            | The number of virtual CPUs allocated to the instance, which affects its computing capabilities.                                   | No       | 1            |                                                                                                                                               |
| `memory_gb`                     | `Optional[float]`            | The amount of memory allocated to the instance, specified in gigabytes (GiB).                                                     | No       | 1            |                                                                                                                                               |
| `region`                        | `Optional[str]`              | The region where the instance is to be deployed, which can affect availability and pricing.                                       | No       | None         | E.g., `us-east-1`, `eu-west-1`                                                                                                                |
| `usage_class`                   | `Optional[UsageClass]`       | The pricing model under which the instance operates: either preemptible `SPOT` instances or regular `ON_DEMAND` instances.        | No       | `on-demand`  | `spot`, `on-demand`                                                                                                                           |
| `burstable`                     | `Optional[bool]`             | Specifies if the instance type can accrue and use CPU credits for short bursts of improved performance.                           | No       | None         | `True`, `False`                                                                                                                               |
| `architecture`                  | `Optional[Architecture]`     | The processor architecture type for the instance, which determines the instruction set and memory addressing.                     | No       | `x86_64`     | `i386`, `x86_64`, `arm64`, `x86_64_mac`                                                                                                      |
| `product_description`           | `Optional[ProductDescription]` | The list of operating systems available for the instance, which may affect compatibility and pricing.                             | No       | `Linux/UNIX` | `Linux/UNIX`, `Red Hat Enterprise Linux`, `SUSE Linux`, `Windows`, `Linux/UNIX (Amazon VPC)`, `Red Hat Enterprise Linux (Amazon VPC)`, `SUSE Linux (Amazon VPC)`, `Windows (Amazon VPC)` |
| `is_current_generation`         | `Optional[bool]`             | Indicates if only the latest generation of instances should be considered, which typically offer better performance and features. | No       | None         | `True`, `False`                                                                                                                               |
| `has_gpu`                       | `Optional[bool]`             | Designates whether the instance includes one or more GPUs, providing additional graphics or computational power.                  | No       | None         | `True`, `False`                                                                                                                               |
| `gpu_memory`                    | `Optional[int]`              | If GPUs are present, this specifies their total memory in GiB. Only applicable when `has_gpu` is True.                            | No       | None         |                                                                                                                                               |
| `gpus`                          | `Optional[int]`              | If GPUs are present, this specifies their total GPUs. Only applicable when `has_gpu` is True.                                     | No       | None         |                                                                                                                                               |
| `is_instance_storage_supported` | `Optional[bool]`             | Determines if the instance should have direct attached storage, often used for high-performance requirements.                     | No       | None         | `True`, `False`                                                                                                                               |
| `max_interruption_frequency`    | `Optional[int]`              | The maximum acceptable spot instance interruption rate, as a percentage (1-100). This helps balance cost with stability.          | No       | None         | E.g., 10                                                                                                                                       |
| `availability_zones`            | `Optional[List[str]]`        | The specific geographic locations in which to search for instances, which can affect latency and data sovereignty considerations. | No       | None         | E.g., `us-east-1a`, `us-east-1b`                                                                                                              |
| `final_spot_price_strategy`     | `Optional[FinalSpotPriceStrategy]` | Strategy used to determine the final spot price, which can optimize for cost or stability of the spot instance.                   | No       | `min`        | `min`, `max`, `average`                                                                                                                       |

# InstanceType (InstanceTypeResponse = List[InstanceType])

| Field                    | Type                                     | Description                                                                                                                | Example Values                                              |
|--------------------------|------------------------------------------|----------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| `instance_type`          | `str`                                    | The identifier for the type of instance, which determines its capabilities, such as CPU and memory.                        | `c5d.large`, `m6idn.large`                                  |
| `price`                  | `float`                                  | The price per hour for the instance type. This could be the on-demand price or the spot price, which can vary based on market demand. | 0.0378, 0.0995                                              |
| `az_price`               | `Optional[Dict[str, float]]`             | A dictionary containing the prices for the instance type within different Availability Zones.                              | `{'us-east-1a': 0.0378, 'us-east-1b': 0.0400}`              |
| `vcpu`                   | `int`                                    | The number of virtual CPUs (vCPUs) provided by the instance type, which affects its processing capability.                 | 2, 4                                                        |
| `memory_gb`              | `int`                                    | The amount of memory (RAM) that the instance type offers, measured in GiB (gibibytes).                                     | 8, 16                                                       |
| `network_performance`    | `str`                                    | A qualitative description of the instance type's network performance capability.                                          | `Up to 10 Gigabit`, `20 Gigabit`                            |
| `storage`                | `Union[str, List[DiskInfo]]`             | Information about the storage that comes with the instance type, including size and type. It could be a list or a descriptive string. | `EBS only`, `[{'SizeInGB': 50, 'Count': 1, 'Type': 'ssd'}]` |
| `gpu_memory_gb`          | `Optional[int]`                          | The amount of dedicated GPU memory that comes with the instance type, if applicable, measured in GiB.                     | 4, 8                                                        |
| `gpus`                   | `Optional[int]`                          | The number of graphical processing units (GPUs) available in the instance type, which can enhance graphics and computational tasks. | 1, 2                                                        |
| `interruption_frequency` | `Optional[InterruptionFrequencyInfo]`    | An estimate of how often a spot instance may be interrupted. It can include statistical rates or qualitative descriptions. | `{'min': 5, 'max': 10, 'rate': '<10%'}`                     |

# Usage

## Simple

```
from best_ec2 import (
    BestEc2,
    InstanceTypeRequest,
    InstanceTypeResponse,
)

ec2 = BestEc2()

request: InstanceTypeRequest = {"vcpu": 1, "memory_gb": 1}

response: InstanceTypeResponse = ec2.get_types(request)

print(response[0:3])
```

Response example:

```json
[
   {
      "instance_type":"t3a.micro",
      "vcpu":2,
      "memory_gb":1,
      "network_performance":"Up to 5 Gigabit",
      "storage":"EBS Only",
      "price":0.0094
   },
   {
      "instance_type":"t3.micro",
      "vcpu":2,
      "memory_gb":1,
      "network_performance":"Up to 5 Gigabit",
      "storage":"EBS Only",
      "price":0.0104
   },
   {
      "instance_type":"t2.micro",
      "vcpu":1,
      "memory_gb":1,
      "network_performance":"Low to Moderate",
      "storage":"EBS Only",
      "price":0.0116
   }
]
```

## Advanced

```
import logging
from botocore.config import Config

from best_ec2 import (
    BestEc2,
    BestEc2Options,
    InstanceTypeRequest,
    InstanceTypeResponse,
    UsageClass,
    Architecture,
    ProductDescription,
    FinalSpotPriceStrategy,
)

options: BestEc2Options = {
    "describe_spot_price_history_concurrency": 20,
    "describe_on_demand_price_concurrency": 15,
    "result_cache_ttl_in_minutes": 120,
    "instance_type_cache_ttl_in_minutes": 2880,
    "on_demand_price_cache_ttl_in_minutes": 720,
    "spot_price_cache_ttl_in_minutes": 5,
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s: %(levelname)s: %(message)s"
)
logger = logging.getLogger()

ec2 = BestEc2(options, logger)

request: InstanceTypeRequest = {
    "vcpu": 1,
    "memory_gb": 2,
    "usage_class": UsageClass.SPOT.value,
    "region": "eu-central-1",
    "burstable": False,
    "architecture": Architecture.X86_64.value,
    "product_description": ProductDescription.LINUX_UNIX.value,
    "is_current_generation": True,
    "is_instance_storage_supported": True,
    "max_interruption_frequency": 0,
    "availability_zones": [
        "eu-central-1a",
        "eu-central-1b",
    ],
    "final_spot_price_strategy": FinalSpotPriceStrategy.MIN.value,
}

request_config: RequestConfig = {
    "ec2_client_config": Config(
        max_pool_connections=20, retries={"max_attempts": 15, "mode": "standard"}
    )
}

response: InstanceTypeResponse = ec2.get_types(request, request_config)

print(response[0:3])
```

Response example:

```json
[
   {
      "instance_type":"i3en.large",
      "vcpu":2,
      "memory_gb":16,
      "network_performance":"Up to 25 Gigabit",
      "storage":[
         {
            "SizeInGB":1250,
            "Count":1,
            "Type":"ssd"
         }
      ],
      "price":0.0332,
      "az_price":{
         "eu-central-1a":0.0396,
         "eu-central-1b":0.0332
      },
      "interruption_frequency":{
         "min":0,
         "max":5,
         "rate":"<5%"
      }
   },
   {
      "instance_type":"c5ad.large",
      "vcpu":2,
      "memory_gb":4,
      "network_performance":"Up to 10 Gigabit",
      "storage":[
         {
            "SizeInGB":75,
            "Count":1,
            "Type":"ssd"
         }
      ],
      "price":0.0426,
      "az_price":{
         "eu-central-1a":0.0426,
         "eu-central-1b":0.0496
      },
      "interruption_frequency":{
         "min":0,
         "max":5,
         "rate":"<5%"
      }
   },
   {
      "instance_type":"c5d.large",
      "vcpu":2,
      "memory_gb":4,
      "network_performance":"Up to 10 Gigabit",
      "storage":[
         {
            "SizeInGB":50,
            "Count":1,
            "Type":"ssd"
         }
      ],
      "price":0.0448,
      "az_price":{
         "eu-central-1b":0.0448,
         "eu-central-1a":0.0459
      },
      "interruption_frequency":{
         "min":0,
         "max":5,
         "rate":"<5%"
      }
   }
]

```
