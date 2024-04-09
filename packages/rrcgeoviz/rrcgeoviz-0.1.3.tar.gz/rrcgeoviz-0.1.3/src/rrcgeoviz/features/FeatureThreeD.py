import numpy as np
import pandas as pd
import panel as pn
from sklearn.cluster import DBSCAN
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature
import plotly.express as px


class FeatureThreeD(ParentGeovizFeature):
    def getOptionName(self):
        return "threeD"

    def getRequiredColumns(self):
        return ["time_column", "latitude_column", "longitude_column"]

    def getHeaderText(self):
        return "Latitude/Longitude/Time 3D Visualization"

    def _generateComponent(self):
        new_df = self.df.copy()
        first_datetime = new_df[self.time_column_name].min()

        new_df["days_int"] = (new_df[self.time_column_name] - first_datetime).dt.days
        lat_min, lat_max = (
            new_df[self.latitude_column_name].min(),
            new_df[self.latitude_column_name].max(),
        )
        long_min, long_max = (
            new_df[self.longitude_column_name].min(),
            new_df[self.longitude_column_name].max(),
        )
        date_min, date_max = new_df["days_int"].min(), new_df["days_int"].max()
        new_df["Normalized_Longitude"] = (
            new_df[self.longitude_column_name] - long_min
        ) / (long_max - long_min)
        new_df["Normalized_Latitude"] = (
            new_df[self.latitude_column_name] - lat_min
        ) / (lat_max - lat_min)
        new_df["Time"] = (new_df["days_int"] - date_min) / (date_max - date_min)
        X = new_df[["Normalized_Longitude", "Normalized_Latitude", "Time"]].dropna()
        db = DBSCAN(eps=0.05, min_samples=5)
        try:
            new_df["cluster"] = db.fit_predict(X)
        except:
            raise TypeError(
                "An error occured trying to cluster for the threeD feature. Most likely, not enough data is available for clustering."
            )
        num_colors = len(new_df)
        colors = np.random.randint(0, 256, size=(num_colors, 3))
        plotly_df = pd.concat(
            [new_df, pd.DataFrame(colors, columns=["r", "g", "b"])], axis=1
        )
        fig = px.scatter_3d(
            plotly_df,
            x="Normalized_Longitude",
            y="Normalized_Latitude",
            z="Time",
            color="cluster",
            color_continuous_scale="solar",
            size_max=10,
        )
        fig.update_layout(scene_aspectmode="auto")
        fig.update_layout(width=800, height=800)

        three_D = pn.Column(fig)

        return three_D
