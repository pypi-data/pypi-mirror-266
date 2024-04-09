import panel as pn
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature
from rrcgeoviz.features.HelpfulFunctions import _emptyScattermap
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class FeatureOneYear(ParentGeovizFeature):
    def getOptionName(self):
        return "one_year"

    def getRequiredColumns(self):
        return ["time_column", "latitude_column", "longitude_column"]

    def getHeaderText(self):
        return "One Year Map"

    def _generateComponent(self):
        desired_year_num = pn.widgets.IntInput(
            name="Enter Year",
            start=self.df["Year"].min(),
            end=self.df["Year"].max(),
            value=self.df["Year"].median().astype("int32"),
            step=1,
        )

        column_dropdown = pn.widgets.Select(
            options=["All"] + self.df.columns.tolist(), name="Columns / Hover Value"
        )

        search_dropdown = pn.widgets.MultiChoice(
            options=["All"],
            name="Select/MultiSelect Key Terms",
        )

        # Make sure to only display options that are found for that year
        def update_options(event):
            column_name = column_dropdown.value
            if column_name == "All":
                unique_values = ["All"]
            else:
                unique_values = (
                    self.df[self.df["Year"] == desired_year_num.value][column_name]
                    .value_counts()
                    .index.tolist()
                )
                unique_values = ["All"] + [
                    val if pd.notna(val) else "NaN" for val in unique_values
                ]
            search_dropdown.options = unique_values

        column_dropdown.param.watch(update_options, "value")
        desired_year_num.param.watch(update_options, "value")

        one_year_plot = pn.bind(
            self._update_one_year_plot,
            new_df=self.df,
            year_value=desired_year_num,
            column_name=column_dropdown,
            filter_value=search_dropdown,
        )

        # Display the dropdowns and initial plot
        one_year = pn.Column(
            desired_year_num,
            pn.Row(column_dropdown, search_dropdown),
            pn.pane.Plotly(one_year_plot, sizing_mode="stretch_width"),
        )

        return one_year

    def _update_one_year_plot(self, new_df, year_value, column_name, filter_value):
        filtered_df = new_df[new_df["Year"] == year_value]

        if filter_value and "All" not in filter_value and column_name != "All":
            filtered_df = filtered_df[filtered_df[column_name].isin(filter_value)]

        if filtered_df.empty:
            return _emptyScattermap()

        hover_data = [column_name] if column_name != "All" else None

        fig = px.scatter_mapbox(
            filtered_df,
            lat=self.latitude_column_name,
            hover_name=self.time_column_name,
            lon=self.longitude_column_name,
            hover_data=hover_data,
            color="Month",
            color_discrete_sequence=px.colors.qualitative.Light24,
            zoom=1,
            height=400,
        )
        fig.update_layout(
            mapbox_style="open-street-map", margin={"r": 20, "t": 20, "l": 20, "b": 20}
        )

        return fig
