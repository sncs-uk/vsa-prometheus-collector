"""
main
~~~~~~~~~~~~

This module runs the prometheus exporter.

:copyright: (c) 2024 by Richard Franks.
:license: Apache2, see LICENSE for more details.
"""
import time
import logging

from starwind_vsa.vsa_client import VsaClient
from prometheus_client import start_http_server
from collectors.disk_collector import DiskCollector
from collectors.pool_collector import PoolCollector
from collectors.volume_collector import VolumeCollector
from collectors.virtual_disk_collector import VirtualDiskCollector

def run(url: str, user: str, password: str, ignore_certs: bool = True) -> None:
    """ Run the exporter """
    print(ignore_certs)
    cl = VsaClient(url, ignore_certs)
    cl.login(user, password)


    common_labels = ['node_name']

    collectors = []

    d = DiskCollector()
    d.define(common_labels)
    collectors.append(d)
    p = PoolCollector()
    p.define(common_labels)
    collectors.append(p)
    v = VolumeCollector()
    v.define(common_labels)
    collectors.append(v)
    vd = VirtualDiskCollector()
    vd.define(common_labels)
    collectors.append(vd)

    start_http_server(9192)
    while True:
        for collector in collectors:
            collector.collect(cl)
        time.sleep(10)


if __name__ == "__main__":
    from dotenv import load_dotenv
    import os

    logging.basicConfig(level=logging.DEBUG)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    logging.getLogger("requests_oauthlib").setLevel(logging.ERROR)

    load_dotenv()
    run(
        os.getenv("VSA_URL"),
        os.getenv("VSA_USER"),
        os.getenv("VSA_PASSWORD"),
        bool(int(os.getenv("IGNORE_CERTS"))))
