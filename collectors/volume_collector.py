"""
collectors.volume_collector
~~~~~~~~~~~~

This module implements a volume collector to collect information about storage volumes.

:copyright: (c) 2024 by Richard Franks.
:license: Apache2, see LICENSE for more details.
"""
from prometheus_client import Gauge, Enum
from starwind_vsa.vsa_client import VsaClient
from collectors.base_collector import BaseCollector

class VolumeCollector(BaseCollector):
    """ Volume collector class """
    def __init__(self):
        super().__init__()
        self._volume_usable_capacity = None
        self._volume_size = None
        self._volume_free_space = None
        self._volume_type = None

    def define(self, common_labels: list) -> None:
        """ Define the metrics to be exported """
        labels = ['volume_name', 'pool_name'] + common_labels

        self._volume_usable_capacity = Gauge("vsa_volume_usable_capacity",
                                             "Volume usable capacity",
                                             labels)
        self._volume_size = Gauge("vsa_volume_size",
                                  "Volume size",
                                  labels)
        self._volume_free_space = Gauge("vsa_volume_free_space",
                                        "Volume free space",
                                        labels)
        self._volume_type = Enum("vsa_volume_type",
                                 "Volume type",
                                 labels,
                                 states=["standard"])

    def collect(self, cl: VsaClient) -> None:
        """ Actually run the collect in order to retreive data"""
        resp = cl.get("api/v1/volumes")

        if resp is None:
            return


        for volume in resp.json()["rows"]:
            self._volume_usable_capacity.labels(
                node_name=volume["nodeName"],
                pool_name=volume["pool"],
                volume_name=volume["volumeName"]
                ).set(volume["usableCapacityBytes"])
            self._volume_size.labels(
                node_name=volume["nodeName"],
                pool_name=volume["pool"],
                volume_name=volume["volumeName"]
                ).set(volume["sizeBytes"])
            self._volume_free_space.labels(
                node_name=volume["nodeName"],
                pool_name=volume["pool"],
                volume_name=volume["volumeName"]
                ).set(volume["freeSpaceBytes"])
            self._volume_type.labels(
                node_name=volume["nodeName"],
                pool_name=volume["pool"],
                volume_name=volume["volumeName"]
                ).state(volume["type"])
