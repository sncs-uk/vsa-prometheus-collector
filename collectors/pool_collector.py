"""
collectors.pool_collector
~~~~~~~~~~~~

This module implements a pool collector to collect information about storage pools.

:copyright: (c) 2024 by Richard Franks.
:license: Apache2, see LICENSE for more details.
"""

from prometheus_client import Gauge, Enum
from starwind_vsa.vsa_client import VsaClient
from collectors.base_collector import BaseCollector

class PoolCollector(BaseCollector):
    """ Pool collector class """
    def __init__(self):
        super().__init__()
        self._pool_raw_capacity = None
        self._pool_usable_capacity = None
        self._pool_free_space = None
        self._pool_type = None
        self._pool_pool_type = None
        self._pool_state = None

    def define(self, common_labels: list) -> None:
        """ Define the metrics to be exported """
        labels = ['pool_name'] + common_labels

        self._pool_raw_capacity = Gauge("vsa_pool_raw_capacity", "Pool raw capacity", labels)
        self._pool_usable_capacity = Gauge("vsa_pool_usable_capacity",
                                           "Pool usable capacity",
                                           labels)
        self._pool_free_space = Gauge("vsa_pool_free_space", "Pool free space", labels)
        # pool_disks = Gauge("vsa_disk_hot_spare", "Disk hot spare", labels)
        self._pool_type = Enum("vsa_pool_type", "Pool type", labels, states=["zfs"])
        self._pool_pool_type = Enum("vsa_pool_pool_type",
                                    "Pool pooling type",
                                    labels,
                                    states=["zfs_stripped_raid_z2"])
        self._pool_state = Enum("vsa_pool_state",
                                "Pool state",
                                labels,
                                states=["online", "offline", "degraded"])

    def collect(self, cl: VsaClient) -> None:
        """ Actually run the collect in order to retreive data"""
        resp = cl.get("api/v1/pools")


        for item in resp.json()["rows"]:
            self._pool_raw_capacity.labels(
                node_name=item["nodeName"],
                pool_name=item["poolName"]
                ).set(item["rawCapacityBytes"])
            self._pool_usable_capacity.labels(
                node_name=item["nodeName"],
                pool_name=item["poolName"]
                ).set(item["usableCapacityBytes"])
            self._pool_free_space.labels(
                node_name=item["nodeName"],
                pool_name=item["poolName"]
                ).set(item["freeSpaceBytes"])
            self._pool_type.labels(
                node_name=item["nodeName"],
                pool_name=item["poolName"]
                ).state(item["type"])
            self._pool_pool_type.labels(
                node_name=item["nodeName"],
                pool_name=item["poolName"]
                ).state(item["poolType"])
            self._pool_state.labels(
                node_name=item["nodeName"],
                pool_name=item["poolName"]
                ).state(item["state"])
