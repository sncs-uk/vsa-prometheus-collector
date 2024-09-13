"""
collectors.disk_collector
~~~~~~~~~~~~

This module implements a disk collector to collect information about physical disks.

:copyright: (c) 2024 by Richard Franks.
:license: Apache2, see LICENSE for more details.
"""

from prometheus_client import Gauge
from starwind_vsa.vsa_client import VsaClient
from collectors.base_collector import BaseCollector

class DiskCollector(BaseCollector):
    """ Disk collector class """
    def __init__(self):
        super().__init__()
        self._disk_used = None
        self._disk_hot_spare = None
        self._disk_size_bytes = None

    def define(self, common_labels: list) -> None:
        """ Define the metrics to be exported """
        labels = ['disk_id'] + common_labels

        self._disk_used = Gauge("vsa_disk_used", "Disk used", labels)
        self._disk_hot_spare = Gauge("vsa_disk_hot_spare", "Disk hot spare", labels)
        self._disk_size_bytes = Gauge("vsa_disk_size_bytes", "Disk size", labels)

    def collect(self, cl: VsaClient) -> None:
        """ Actually run the collect in order to retreive data"""
        resp = cl.get("api/v1/disks")

        if resp is None:
            return


        for item in resp.json()["rows"]:
            self._disk_used.labels(
                node_name=item["nodeName"],
                disk_id=item["id"]
                ).set(item["used"])
            self._disk_hot_spare.labels(
                node_name=item["nodeName"],
                disk_id=item["id"]
                ).set(item["hotSpare"])
            self._disk_size_bytes.labels(
                node_name=item["nodeName"],
                disk_id=item["id"]
                ).set(item["sizeBytes"])
