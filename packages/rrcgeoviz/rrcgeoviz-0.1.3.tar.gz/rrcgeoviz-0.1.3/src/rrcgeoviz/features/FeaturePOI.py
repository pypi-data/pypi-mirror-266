import panel as pn
from rrcgeoviz.features.ParentGeovizFeature import ParentGeovizFeature


class FeaturePOI(ParentGeovizFeature):
    def getOptionName(self):
        return "poi_analysis"

    def getRequiredColumns(self):
        return ["latitude_column", "longitude_column"]

    def getHeaderText(self):
        return "Most popular Points of Interest (POI)"

    def _generateComponent(self):
        poi_df = self.generated_data.data_dict["poi_analysis"][
            ["name", "port_lat", "port_long", "num_points"]
        ]
        poi_df = poi_df.rename(
            columns={
                "name": "Name",
                "port_lat": "Latitude",
                "port_long": "Longitude",
                "num_points": "# of nearby incidents",
            }
        )
        poi_app = pn.Column(pn.pane.DataFrame(poi_df, max_rows=20, index=False))
        # Show the Panel app
        return poi_app
