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
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingContext,
                       QgsProcessingParameterDefinition,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterString,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingFeedback
                       )
from typing import Any

from PyQt5.QtGui import QIcon

from ORStools import RESOURCE_PREFIX, __help__
from ORStools.utils import configmanager
from ..common import client, PROFILES, AVOID_BORDERS, AVOID_FEATURES, ADVANCED_PARAMETERS
from ..utils.processing import read_help_file
from ..gui.directions_gui import _get_avoid_polygons


# noinspection PyPep8Naming
class ORSBaseProcessingAlgorithm(QgsProcessingAlgorithm):
    """Base algorithm class for ORS algorithms"""

    def __init__(self):
        """
        Default attributes used in all child classes
        """
        super().__init__()
        self.ALGO_NAME = ''
        self.GROUP = ''
        self.IN_PROVIDER = "INPUT_PROVIDER"
        self.IN_PROFILE = "INPUT_PROFILE"
        self.IN_AVOID_FEATS = "INPUT_AVOID_FEATURES"
        self.IN_AVOID_BORDERS = "INPUT_AVOID_BORDERS"
        self.IN_AVOID_COUNTRIES = "INPUT_AVOID_COUNTRIES"
        self.IN_AVOID_POLYGONS = "INPUT_AVOID_POLYGONS"
        self.OUT = 'OUTPUT'
        self.PARAMETERS = None

    def createInstance(self) -> Any:
        """
        Returns instance of any child class
        """
        return self.__class__()

    def group(self) -> str:
        """
        Returns group name (Directions, Isochrones, Matrix) defined in child class
        """
        return self.GROUP

    def groupId(self) -> str:
        return self.GROUP.lower()

    def name(self) -> str:
        """
        Returns algorithm name defined in child class
        """
        return self.ALGO_NAME

    def shortHelpString(self):
        """
        Displays the sidebar help in the algorithm window
        """
        return read_help_file(file_name=f'{self.ALGO_NAME}.help')

    @staticmethod
    def helpUrl():
        """
        Will be connected to the Help button in the Algorithm window
        """
        return __help__

    def displayName(self) -> str:
        """
        Algorithm name shown in QGIS toolbox
        :return:
        """
        return self.ALGO_NAME.capitalize().replace('_', ' ')

    def icon(self) -> QIcon:
        """
        Icon used for algorithm in QGIS toolbox
        """
        return QIcon(RESOURCE_PREFIX + f'icon_{self.groupId()}.png')

    def provider_parameter(self) -> QgsProcessingParameterEnum:
        """
        Parameter definition for provider, used in all child classes
        """
        providers = [provider['name'] for provider in configmanager.read_config()['providers']]
        return QgsProcessingParameterEnum(
            self.IN_PROVIDER,
            "Provider",
            providers,
            defaultValue=providers[0]
        )

    def profile_parameter(self) -> QgsProcessingParameterEnum:
        """
        Parameter definition for profile, used in all child classes
        """
        return QgsProcessingParameterEnum(
                self.IN_PROFILE,
                "Travel mode",
                PROFILES,
                defaultValue=PROFILES[0]
            )

    def output_parameter(self) -> QgsProcessingParameterFeatureSink:
        """
        Parameter definition for output, used in all child classes
        """
        return QgsProcessingParameterFeatureSink(
            name=self.OUT,
            description=self.GROUP,
        )

    def option_parameters(self) -> [QgsProcessingParameterDefinition]:
        return [
            QgsProcessingParameterEnum(
                self.IN_AVOID_FEATS,
                "Features to avoid",
                AVOID_FEATURES,
                defaultValue=None,
                optional=True,
                allowMultiple=True
            ),
            QgsProcessingParameterEnum(
                self.IN_AVOID_BORDERS,
                "Types of borders to avoid",
                AVOID_BORDERS,
                defaultValue=None,
                optional=True
            ),
            QgsProcessingParameterString(
                self.IN_AVOID_COUNTRIES,
                "Comma-separated list of ids of countries to avoid",
                defaultValue=None,
                optional=True
            ),
            QgsProcessingParameterFeatureSource(
                self.IN_AVOID_POLYGONS,
                "Polygons to avoid",
                types=[QgsProcessing.TypeVectorPolygon],
                optional=True
            )
        ]

    @staticmethod
    def _get_ors_client_from_provider(provider: str, feedback: QgsProcessingFeedback) -> client.Client:
        """
        Connects client to provider and returns a client instance for requests to the ors API
        """
        providers = configmanager.read_config()['providers']
        ors_provider = providers[provider]
        ors_client = client.Client(ors_provider)
        ors_client.overQueryLimit.connect(lambda: feedback.reportError("OverQueryLimit: Retrying..."))
        return ors_client

    def parseOptions(self, parameters: dict, context: QgsProcessingContext) -> dict:
        options = dict()

        features_raw = parameters[self.IN_AVOID_FEATS]
        if features_raw:
            options['avoid_features'] = [dict(enumerate(AVOID_FEATURES))[feat] for feat in features_raw]

        borders_raw = parameters[self.IN_AVOID_BORDERS]
        if borders_raw:
            options['avoid_borders'] = dict(enumerate(AVOID_BORDERS))[borders_raw]

        countries_raw = parameters[self.IN_AVOID_COUNTRIES]
        if countries_raw:
            options['avoid_countries'] = list(map(int, countries_raw.split(',')))

        polygons_layer = self.parameterAsLayer(parameters, self.IN_AVOID_POLYGONS, context)
        if polygons_layer:
            options['avoid_polygons'] = _get_avoid_polygons(polygons_layer)

        return options

    # noinspection PyUnusedLocal
    def initAlgorithm(self, configuration):
        """
        Combines default and algorithm parameters and adds them in order to the
        algorithm dialog window.
        """
        parameters = [self.provider_parameter(), self.profile_parameter()] + self.PARAMETERS + self.option_parameters() + [self.output_parameter()]
        for param in parameters:
            if param.name() in ADVANCED_PARAMETERS:
                if self.GROUP == "Matrix":
                    param.setFlags(param.flags()| QgsProcessingParameterDefinition.FlagHidden)
                else:
                    # flags() is a wrapper around an enum of ints for type-safety.
                    # Flags are added by or-ing values, much like the union operator would work
                    param.setFlags(param.flags() | QgsProcessingParameterDefinition.FlagAdvanced)

            self.addParameter(
                param
            )
