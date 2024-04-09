import datetime
from matplotlib import pyplot as plt
import pandas as pd
import panel as pn
import seaborn as sns
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature
from rrcgeoviz.arguments import Arguments

import rrcgeoviz


class FeatureOneYearMonths(ParentGeovizFeature):
    def getOptionName(self):
        return "one_year_months"

    def getRequiredColumns(self):
        return ["time_column", "latitude_column", "longitude_column"]

    def getHeaderText(self):
        return "Month-to-Month Frequency for One Year"

    def _generateComponent(self):
        desired_year = pn.widgets.IntInput(
            name="Enter Year",
            start=self.df["Year"].min(),
            end=self.df["Year"].max(),
            value=int(self.df["Year"].median()),
            step=1,
        )
        year_months_plot = pn.bind(self._update_year_months_plot, value=desired_year)

        one_year_months = pn.Column(
            desired_year,
            pn.panel(year_months_plot),
        )
        return one_year_months

    def _update_year_months_plot(self, value):
        desired_year = value
        filtered_df = self.df[self.df["Year"] == desired_year]
        fig, ax = plt.subplots(figsize=(8, 4))
        sns.set_theme(style="whitegrid")
        month_order = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        sns.countplot(
            data=filtered_df, x="Month", order=month_order, palette="colorblind"
        )
        plt.xlabel("Month")
        plt.ylabel("Frequency")
        plt.title(f"Incidents by Month for Year {desired_year}")

        out = plt.gcf()
        return out
