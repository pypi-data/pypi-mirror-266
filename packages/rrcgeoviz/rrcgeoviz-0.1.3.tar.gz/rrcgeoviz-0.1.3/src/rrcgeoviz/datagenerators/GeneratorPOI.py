import datetime
import os
import warnings
import pandas as pd
import geopy.distance
from tqdm import tqdm
from rrcgeoviz.arguments import Arguments
from rrcgeoviz.datagenerators.ParentDataGenerator import ParentDataGenerator
from geolib import geohash
from geopy.geocoders import Nominatim

MAX_RANGE_MILES = 5
# Uses precision=4 so goes up to ~40, see https://gis.stackexchange.com/questions/115280/what-is-the-precision-of-geohash


class GeneratorPOI(ParentDataGenerator):
    def __init__(self, args: Arguments) -> None:
        super().__init__(args)
        self.geolocator = Nominatim(user_agent="GeoViz")

    def getOptionName(self):
        return "poi_analysis"

    def generateData(self):
        print("Generating POI data...")
        port_df = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "data", "ports.csv")
        )
        self.data["geohash"] = self.data.apply(self.encode_data, axis=1)
        port_df["geohash"] = port_df.apply(self.encode_ports, axis=1)
        port_df["num_points"] = port_df.apply(
            self.num_points, axis=1, range=MAX_RANGE_MILES
        )
        out = port_df.sort_values("num_points", ascending=False)
        return out

    def calculate_distance(self, row, port_lat, port_long, range):
        if isinstance(row[self.columns["latitude_column"]], float) and isinstance(
            row[self.columns["longitude_column"]], float
        ):
            return (
                geopy.distance.geodesic(
                    (
                        row[self.columns["latitude_column"]],
                        row[self.columns["longitude_column"]],
                    ),
                    (port_lat, port_long),
                ).miles
                < range
            )
        else:
            return 99999999

    def encode_data(self, row):
        try:
            if isinstance(row[self.columns["latitude_column"]], float) and isinstance(
                row[self.columns["longitude_column"]], float
            ):
                hash = geohash.encode(
                    row[self.columns["latitude_column"]],
                    row[self.columns["longitude_column"]],
                    4,
                )
                return hash
            else:
                return ""
        except:
            warnings.warn(
                "A row's coordinates were unable to be hashed into GeoHash, ignoring coordinates "
                + str(self.columns["latitude_column"])
                + " "
                + str(self.columns["longitude_column"]),
                UserWarning,
            )

    def encode_ports(self, row):
        return geohash.encode(
            row["port_lat"],
            row["port_long"],
            4,
        )

    def num_points(self, row, range=5):
        squares = list(geohash.neighbours(row["geohash"]))
        squares.append(row["geohash"])
        # Only get the rows where it's in the neighboring squares
        filtered_df = self.data[self.data["geohash"].isin(squares)]
        port_lat_var = row["port_lat"]
        if len(filtered_df) > 0:
            filtered_df = filtered_df[
                filtered_df.apply(
                    self.calculate_distance,
                    axis=1,
                    port_long=row["port_long"],
                    port_lat=port_lat_var,
                    range=range,
                )
            ]
        out = len(filtered_df)
        return out
