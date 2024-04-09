import panel as pn
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature
from rrcgeoviz.features.HelpfulFunctions import _emptyScattermap
import plotly.express as px
import pandas as pd


class FeatureYearlyRange(ParentGeovizFeature):
    def getOptionName(self):
        return "yearly_range"

    def getRequiredColumns(self):
        return ["time_column", "latitude_column", "longitude_column"]

    def getHeaderText(self):
        return "Year Range Map"

    def _generateComponent(self):
        year_range_slider = pn.widgets.RangeSlider(
            name="Select Year Range",
            start=self.df["Year"].min(),
            end=self.df["Year"].max(),
            value=(self.df["Year"].min(), self.df["Year"].max()),
            step=1,
        )

        column_dropdown = pn.widgets.Select(
            options=["All"] + self.df.columns.tolist(), name="Columns / Hover Value"
        )

        search_dropdown = pn.widgets.MultiChoice(
            options=["All"],
            name="Select/MultiSelect Key Terms",
        )

        def update_options(event):
            column_name = column_dropdown.value
            if column_name == "All":
                unique_values = ["All"]
            else:
                selected_years = year_range_slider.value
                filtered_df = self.df[
                    (self.df["Year"] >= selected_years[0])
                    & (self.df["Year"] <= selected_years[1])
                ]
                unique_values = filtered_df[column_name].value_counts().index.tolist()
                unique_values = ["All"] + [
                    val if pd.notna(val) else "NaN" for val in unique_values
                ]
                search_dropdown.options = unique_values

        column_dropdown.param.watch(update_options, "value")
        year_range_slider.param.watch(update_options, "value")

        yearly_range_plot = pn.bind(
            self._update_yearly_range_plot,
            new_df=self.df,
            years_value=year_range_slider,
            column_name=column_dropdown,
            filter_value=search_dropdown,
        )

        yearly_range = pn.Column(
            year_range_slider,
            pn.Row(column_dropdown, search_dropdown),
            pn.pane.Plotly(yearly_range_plot, sizing_mode="stretch_width"),
        )

        return yearly_range

    def _update_yearly_range_plot(self, new_df, years_value, column_name, filter_value):
        min_year, max_year = years_value
        filtered_df = new_df[
            (new_df["Year"] >= min_year) & (new_df["Year"] <= max_year)
        ]
        if filter_value and "All" not in filter_value and column_name != "All":
            filtered_df = filtered_df[filtered_df[column_name].isin(filter_value)]

        if filtered_df.empty:
            return _emptyScattermap()

        hover_data = [column_name] if column_name != "All" else []

        fig = px.scatter_mapbox(
            filtered_df,
            lat=self.latitude_column_name,
            hover_name=self.time_column_name,
            lon=self.longitude_column_name,
            hover_data=hover_data,
            color="Year",
            zoom=1,
            height=400,
        )
        fig.update_layout(
            mapbox_style="open-street-map", margin={"r": 20, "t": 20, "l": 20, "b": 20}
        )
        return fig
