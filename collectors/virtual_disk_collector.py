"""
collectors.virtual_disk_collector
~~~~~~~~~~~~

This module implements a virtual disk collector to collect information about virtual disks.

:copyright: (c) 2024 by Richard Franks.
:license: Apache2, see LICENSE for more details.
"""

from prometheus_client import Info, Gauge, Enum
from starwind_vsa.vsa_client import VsaClient
from collectors.base_collector import BaseCollector

class VirtualDiskCollector(BaseCollector):
    """ Virtual Disk collector class """
    def __init__(self):
        super().__init__()
        self._availability = None
        self._synchronization_state = None
        self._synchronized_bytes = None
        self._not_synchronized_bytes = None
        self._synchronized_percent = None
        self._synchronization_estimated_time = None
        self._sessions = None

    def define(self, common_labels: list) -> None:
        """ Define the metrics to be exported """
        labels = ["serial_id", "lun", "name"] + common_labels

        self._availability = Enum("vsa_virtual_disk_availability",
                                  "Virtual disk availability",
                                  labels,
                                  states=["simple", "limited_availability", "highly_available"])
        self._synchronization_state = Enum("vsa_virtual_disk_synchronization_state",
                                           "Virtual disk synchronization state",
                                           labels,
                                           states=["notApplicable",
                                                   "synchronizing",
                                                   "synchronized"])
        self._synchronized_bytes = Gauge("vsa_virtual_disk_synchronized_bytes",
                                         "Virtual disk synchronized bytes",
                                         labels)
        self._not_synchronized_bytes = Gauge("vsa_virtual_disk_not_synchronized_bytes",
                                             "Virtual disk not synchronized bytes",
                                             labels)
        self._synchronized_percent = Gauge("vsa_virtual_disk_synchronized_percent",
                                           "Virtual disk synchronized percentage",
                                           labels)
        self._synchronization_estimated_time = Gauge(
                                        "vsa_virtual_disk_synchronization_estimated_time",
                                        "Virtual disk synchronization estimated time",
                                        labels)
        self._sessions = Info("vsa_virtual_disk_session",
                              "Virtual disk session",
                              labels + ["session_id"])

    def collect(self, cl: VsaClient) -> None:
        """ Actually run the collect in order to retreive data"""
        resp = cl.get("api/v1/virtualdisks")

        if resp is None:
            return


        for item in resp.json()["rows"]:
            self._availability.labels(
                node_name=item["nodeName"],
                serial_id=item["serialId"],
                lun=item["iscsiLun"],
                name=item["name"]
                ).state(item["availability"])
            self._synchronization_state.labels(
                node_name=item["nodeName"],
                serial_id=item["serialId"],
                lun=item["iscsiLun"],
                name=item["name"]
                ).state(item["synchronizationState"]["syncStatus"])
            self._synchronized_bytes.labels(
                node_name=item["nodeName"],
                serial_id=item["serialId"],
                lun=item["iscsiLun"],
                name=item["name"]
                ).set(item["synchronizationState"]["synchronizedBytes"])
            self._not_synchronized_bytes.labels(
                node_name=item["nodeName"],
                serial_id=item["serialId"],
                lun=item["iscsiLun"],
                name=item["name"]
                ).set(item["synchronizationState"]["notSynchronizedBytes"])
            self._synchronized_percent.labels(
                node_name=item["nodeName"],
                serial_id=item["serialId"],
                lun=item["iscsiLun"],
                name=item["name"]
                ).set(item["synchronizationState"]["synchronizedPercents"])
            self._synchronization_estimated_time.labels(
                node_name=item["nodeName"],
                serial_id=item["serialId"],
                lun=item["iscsiLun"],
                name=item["name"]
                ).set(item["synchronizationState"]["estimatedTimeSecond"])
            for appliance in item["appliances"]:
                for session in appliance["sessionAndACLs"]:
                    session_stripped = {}
                    for k in session:
                        session_stripped[k] = str(session[k])
                    self._sessions.labels(
                        node_name=item["nodeName"],
                        serial_id=item["serialId"],
                        lun=item["iscsiLun"],
                        name=item["name"],
                        session_id=session["id"]
                        ).info(session_stripped)
