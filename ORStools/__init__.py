# -*- coding: utf-8 -*-
"""
/***************************************************************************
 ORStools
                                 A QGIS plugin
 falk
                             -------------------
        begin                : 2017-02-01
        copyright            : (C) 2017 by nils
        email                : nils
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os.path
import configparser
from datetime import datetime


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load OSMtools class from file OS;tools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .ORStoolsPlugin import ORStools
    return ORStools(iface)


# Define plugin wide constants
PLUGIN_NAME = 'ORS Tools'
DEFAULT_COLOR = '#a8b1f5'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(BASE_DIR, 'static', 'img')
CONFIG_PATH = os.path.join(BASE_DIR, 'config.yml')
ENV_VARS = {'ORS_REMAINING': 'X-Ratelimit-Remaining',
            'ORS_QUOTA': 'X-Ratelimit-Limit'}
ENDPOINTS = {'isochrones': '/isochrones',
             'directions': '/directions',
             'matrix': '/matrix',
             'geocoding': 'geocoding'}

# Read metadata.txt
METADATA = configparser.ConfigParser()
METADATA.read(os.path.join(BASE_DIR, 'metadata.txt'))
today = datetime.today()

__version__ = METADATA['general']['version']
__author__ = METADATA['general']['author']
__email__ = METADATA['general']['email']
__web__ = METADATA['general']['homepage']
__help__ = METADATA['general']['help']
__date__ = today.strftime('%Y-%m-%d')
__copyright__ = '(C) {} by {}'.format(today.year, __author__)
