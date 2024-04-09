import os
import string
import threading
from time import sleep
import time
from bertopic import BERTopic
import pandas as pd
import panel as pn
from bokeh.models import Div
from rrcgeoviz.features.FeatureBertMap import FeatureBertMap
from rrcgeoviz.features.FeatureOneYearMonths import FeatureOneYearMonths
from rrcgeoviz.features.FeatureOneYear import FeatureOneYear
from rrcgeoviz.features.FeatureAllMonths import FeatureAllMonths
from rrcgeoviz.features.FeatureHeatmap import FeatureHeatmap
from rrcgeoviz.features.FeatureThreeD import FeatureThreeD
from rrcgeoviz.features.FeatureYearlyRange import FeatureYearlyRange
from rrcgeoviz.features.Downloadables import gen_profile_report
from rrcgeoviz.features.FeaturePOI import FeaturePOI
from rrcgeoviz.features.FeatureSearch import FeatureSearch
from rrcgeoviz.features.FeatureBertopic import FeatureBertopic
from rrcgeoviz.features.FeatureWordCloud import FeatureWordCloud
from rrcgeoviz.features.FeartureDataFrameEditor import FeatureDataFrameEditor
import warnings
from rrcgeoviz.arguments import Arguments

from panel.widgets.indicators import BooleanIndicator
from dateutil.parser import parse
from panel.io import server

pn.extension(nthreads=0)

import importlib.resources
from pandas.api.types import is_string_dtype
from pandas.api.types import is_numeric_dtype

LOGO_PATH = "https://i.imgur.com/Loud9RB.jpeg"
FAVICON_PATH = "https://i.imgur.com/x0JaYkq.png"

FEATURE_CLASSES = [
    FeatureHeatmap,
    FeatureYearlyRange,
    FeatureOneYear,
    FeatureAllMonths,
    FeatureOneYearMonths,
    FeatureThreeD,
    FeaturePOI,
    FeatureSearch,
]

NLP_FEATURE_CLASSES = [
    FeatureBertopic,
    FeatureBertMap,
    FeatureWordCloud,
]


class GeoVizPanelDashboard:
    def __init__(self, args: Arguments, test=False) -> None:
        self.test = test
        self.args = args
        self.columns = self.args.getColumns()
        self.data = self.args.getData()
        self.features = self.args.getFeatures()
        self.data = self.verifyDataFormat()
        self.data = self.modify_columns()
        self.generated_data = self.args.generated_data
        self.dashboard = self.create_template(args)

    def render(self):
        if not self.test:
            pn.serve(self.dashboard)

    def verifyDataFormat(self) -> pd.DataFrame:
        self._verifyDataColumnsExist()
        self._warnIfNanExists()
        self._verifyCanParseDates()
        self._verifyLatLongArePossible()
        self._verifyFeatureCustomizationColumnsExist()
        return self.data

    def _verifyFeatureCustomizationColumnsExist(self):
        # TODO: Make this easier to extend without trying to rememer which options are available.
        # Maybe iterate through a function in every feature that lists its customizations?
        customizations = self.args.getFeatureCustomizations()

        if "hover_text_columns" in customizations:
            for col in customizations["hover_text_columns"]:
                if col not in self.data.columns:
                    raise TypeError("Hover text column not found: " + col)

        if "filter_one_year_column" in customizations:
            if customizations["filter_one_year_column"] not in self.data.columns:
                raise TypeError(
                    "Filter one year column not found: "
                    + customizations["filter_one_year_column"]
                )

    def _verifyCanParseDates(self):
        try:
            pd.to_datetime(self.data[self.columns["time_column"]])
        except:
            raise TypeError(
                "The given time column can't be parsed into datetime format."
            )

    def _verifyLatLongArePossible(self):
        if not is_numeric_dtype(self.data[self.columns["latitude_column"]]):
            raise TypeError("The given latitude column is non-numeric.")

        if not is_numeric_dtype(self.data[self.columns["longitude_column"]]):
            raise TypeError("The given longitude column is non-numeric.")

        if not ((self.data[self.columns["latitude_column"]] > -90).all()):
            raise TypeError("There are latitude values below -90.")
        if not ((self.data[self.columns["latitude_column"]] < 90).all()):
            raise TypeError("There are latitude values above 90.")

        if not ((self.data[self.columns["longitude_column"]] > -180).all()):
            raise TypeError("There are latitude values below -180.")
        if not ((self.data[self.columns["longitude_column"]] < 180).all()):
            raise TypeError("There are latitude values above 180.")

    def _warnIfNanExists(self):
        error_message = "A null value was found in the dataset. GeoViz ignores any rows with null values in the latitude, longitude, or date columns."
        relevant_data = self.data[self.columns.values()]
        null_columns = relevant_data.isnull().any()
        already_warned = False
        for col_name, is_null in null_columns.items():
            # index, 0
            if is_null and not already_warned:
                already_warned = True
                warnings.warn(error_message, UserWarning)
                self.data.dropna(subset=[col_name], inplace=True)

        return self.data

    def _verifyDataColumnsExist(self):
        error_message = "An incorrect column name was given. Check for misspellings and different capitalizations in the columns options section."
        if "time_column" in self.columns:
            if self.columns["time_column"] not in self.data.columns:
                raise TypeError(error_message)

        if "latitude_column" in self.columns:
            if self.columns["latitude_column"] not in self.data.columns:
                raise TypeError(error_message)

        if "longitude_column" in self.columns:
            if self.columns["longitude_column"] not in self.data.columns:
                raise TypeError(error_message)

        if "description_column" in self.columns:
            if self.columns["description_column"] not in self.data.columns:
                raise TypeError(error_message)

    def modify_columns(self):
        if "time_column" in self.columns:
            self.data[self.columns["time_column"]] = pd.to_datetime(
                self.data[self.columns["time_column"]]
            )
        return self.data

    def create_template(self, args: Arguments):
        template = pn.template.BootstrapTemplate(
            title="GeoViz - " + str(args.getDataFileName()),
            collapsed_sidebar=True,
            logo=LOGO_PATH,
            favicon=FAVICON_PATH,
        )
        mainColumn = pn.Column()
        nlpColumn = pn.Column()
        mainColumn = self.addCorrectElements(args, mainColumn, FEATURE_CLASSES)
        nlpColumn = self.addCorrectElements(args, nlpColumn, NLP_FEATURE_CLASSES)

        template.main.append(
            pn.Tabs(
                ("Visualizations", mainColumn),
                ("Natural Language", nlpColumn),
                (
                    "DataFrame Editor",
                    pn.Column(FeatureDataFrameEditor(args).generateFeature()),
                ),
                ("Downloadables", pn.Column(gen_profile_report(args))),
            )
        )

        return template

    def addCorrectElements(self, arguments: Arguments, mainColumn, classes):
        """Actually add the right elements to the display.
        A dictionary of generated data and the arguments are available for purchase at the gift store.
        """
        for featureType in classes:
            feature = featureType(arguments)
            if feature.getOptionName() in self.features:
                for required_column in feature.getRequiredColumns():
                    if required_column not in self.columns:
                        raise TypeError(
                            "Column "
                            + required_column
                            + " is required for "
                            + feature.getOptionName()
                        )

                mainColumn.append(
                    pn.pane.HTML("<h2>" + feature.getHeaderText() + "</h2>")
                )
                mainColumn.append(feature.generateFeature())

        return mainColumn
