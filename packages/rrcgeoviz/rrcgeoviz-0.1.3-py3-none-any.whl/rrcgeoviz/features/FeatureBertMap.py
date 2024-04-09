import panel as pn
from rrcgeoviz.features.HelpfulFunctions import _emptyScattermap
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature
import plotly.express as px
import plotly.graph_objects as go


class FeatureBertMap(ParentGeovizFeature):
    def getOptionName(self):
        return "nlp_bertopics"

    def getRequiredColumns(self):
        return ["description_column"]

    def getHeaderText(self):
        return "Bertopics Plot"

    def _generateComponent(self):
        year_slider = pn.widgets.RangeSlider(
            name="Select Year",
            start=self.df["Year"].min(),
            end=self.df["Year"].max(),
            value=(self.df["Year"].min(), self.df["Year"].max()),
            step=1,
        )

        unique_values = self.df["BERTopic_label"].value_counts().index.tolist()
        unique_values = ["All"] + unique_values
        dropdown = pn.widgets.Select(
            value=unique_values[0], options=unique_values, name="BerTopic Label"
        )

        bert_map_plot = pn.bind(
            self._update_plot,
            new_df=self.df,
            year_value=year_slider,
            filter_value=dropdown,
        )

        bert_map = pn.Column(
            year_slider,
            dropdown,
            pn.pane.Plotly(bert_map_plot, sizing_mode="stretch_width"),
        )

        return bert_map

    def _update_plot(self, new_df, year_value, filter_value):
        min_year, max_year = year_value
        filtered_df = new_df[
            (new_df["Year"] >= min_year) & (new_df["Year"] <= max_year)
        ]
        if filter_value != "All":
            filtered_df = filtered_df[filtered_df["BERTopic_label"] == filter_value]

        if filtered_df.empty:
            return _emptyScattermap()

        filtered_df["BERTopic_label"] = filtered_df["BERTopic_label"].astype("category")

        fig = px.scatter_mapbox(
            filtered_df,
            lat=self.latitude_column_name,
            lon=self.longitude_column_name,
            hover_name=self.time_column_name,
            color="BERTopic_label",
            color_discrete_sequence=px.colors.qualitative.Dark24,
            zoom=1,
            height=400,
        )
        fig.update_layout(
            mapbox_style="open-street-map", margin={"r": 20, "t": 20, "l": 20, "b": 20}
        )

        return fig
