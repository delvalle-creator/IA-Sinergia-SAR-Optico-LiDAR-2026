# -*- coding: utf-8 -*-
"""NISAR GCOV Reader - punto de entrada del complemento QGIS."""


def classFactory(iface):
    from .nisar_gcov_plugin import NisarGcovReaderPlugin
    return NisarGcovReaderPlugin(iface)
