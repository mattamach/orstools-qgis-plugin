# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ORStools
                                 A QGIS plugin
 QGIS client to query openrouteservice
                              -------------------
        begin                : 2017-02-01
        git sha              : $Format:%H$
        copyright            : (C) 2021 by HeiGIT gGmbH
        email                : support@openrouteservice.heigit.org
 ***************************************************************************/

 This plugin provides access to openrouteservice API functionalities
 (https://openrouteservice.org), developed and
 maintained by the openrouteservice team of HeiGIT gGmbH, Germany. By using
 this plugin you agree to the ORS terms of service
 (https://openrouteservice.org/terms-of-service/).

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import QgsApplication

from .gui import ORStoolsDialog
from .proc import provider


class ORStools:
    """QGIS Plugin Implementation."""
    # noinspection PyTypeChecker,PyArgumentList,PyCallByClass

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.dialog = ORStoolsDialog.ORStoolsDialogMain(iface)
        self.provider = provider.ORStoolsProvider()

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        QgsApplication.processingRegistry().addProvider(self.provider)
        self.dialog.initGui()

    def unload(self):
        """remove menu entry and toolbar icons"""
        QgsApplication.processingRegistry().removeProvider(self.provider)
        self.dialog.unload()
