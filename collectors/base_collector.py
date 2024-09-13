"""
collectors.base_collector
~~~~~~~~~~~~

This module implements a base collector class to be inherited.

:copyright: (c) 2024 by Richard Franks.
:license: Apache2, see LICENSE for more details.
"""
from starwind_vsa.vsa_client import VsaClient

class BaseCollector:
    """ Base collector class """
    def define(self, common_labels: list) -> None:
        """ Define the metrics to be exported """

    def collect(self, cl: VsaClient) -> None:
        """ Actually run the collect in order to retreive data"""
