import io
import json
import string
import typing
import pandas as pd
from pandas.errors import EmptyDataError

spec = """
Arguments() takes two parameters:
- csvFile: a text file object ending in .csv, see https://docs.python.org/3/glossary.html#term-text-file
- jsonFile: a text file object ending in .json
These are made either by argparse or with open().
- if either is not a valid file path or is empty, an error is thrown.
- csvFile must be able to be read with read_csv and jsonFile with json.load, else an error is thrown.
- the json file must have a columns section and features section. It may have a caching and features_customizations section.
Any other section or lack of columns/features causes an error to be thrown.

RESUME FROM HERE
- the Columns section must be a dictionary, with ALL of these keys: "latitude_column","longitude_column","time_column" and an optional "description_column"
Any others throws an error. All keys must have a non-null string value.All keys must be a column name found in the csv file.
- the Features must be an array with only have approved feature names (strings). Any others throws an error.
- caching, if exists, must be a dictionary with a cache_results key (boolean value), use_cache key (boolean), and a cache_location key (string value)
- if caching does not exist, a default is assumed:
"caching": {
        "cache_results": false,
        "use_cache": false,
        "cache_location": "./.geovizcache"
    }
- cache_location must be a valid path. In addition, geoviz must have permission to make a folder at that location, if needed.
- if features_customizations exists, must be a dict, and can only have "hover_text_columns": List[string], "filter_one_year_column": string.
All strings must be valid column names.

- any rows with a null value in required columns will be dropped. Null values in description column will become an empty string.
- all column values in latitude_column must be float values between x and x.
- all longitude_column values must be floats between x and x.
- time_column must be all parseable with gettime() or whatever it is
- description column, if set, must be all strings.



"""


class Arguments:
    generated_data = {}
    _columns = {}
    _features = {}
    _caching = {}
    _feature_customizations = {}

    def __init__(self, csvFile, jsonFile) -> None:
        self._verifyFiles(csvFile, jsonFile)

        self._data = self._loadData(csvFile, ".csv", "data", pd.read_csv)
        print("Data loaded...")
        self.options = self._loadData(jsonFile, ".json", "options", json.load)
        print("Options loaded...")

        self._verifyJson()

        self._columns = self.options["columns"]
        self._features = self.options["features"]
        if "caching" in self.options:
            self._caching = self.options["caching"]
        else:
            self._caching = {
                "cache_results": False,
                "use_cache": False,
            }
        if "features_customizations" in self.options:
            self._feature_customizations = self.options["features_customizations"]
        self._data_file_name = csvFile.name

    def _verifyJson(self):
        if not "columns" in self.options:
            raise TypeError("JSON Config file missing 'columns' dictionary.")
        if not "features" in self.options:
            raise TypeError("JSON Config file missing 'features' array.")

        allowed_sections = ["columns", "features", "caching", "features_customizations"]
        for key in self.options.keys():
            if key not in allowed_sections:
                raise TypeError("Unrecognized section found in JSON: " + key)

    def _verifyFiles(self, csvFile, jsonFile):
        if (not isinstance(csvFile, typing.TextIO)) and (
            not isinstance(csvFile, io.TextIOWrapper)
        ):
            print(type(csvFile))
            raise TypeError("Wrong file types passed to Arguments.")
        if (not isinstance(jsonFile, typing.TextIO)) and (
            not isinstance(jsonFile, io.TextIOWrapper)
        ):
            print(type(csvFile))
            raise TypeError("Wrong file types passed to Arguments.")

        self._checkIsEmptyFile(csvFile)
        self._checkIsEmptyFile(jsonFile)

    def _checkIsEmptyFile(self, my_file):
        my_file.seek(0)  # Ensure you're at the start of the file..
        first_char = my_file.read(1)  # Get the first character
        if not first_char:
            raise TypeError("File is blank.")
        else:
            my_file.seek(
                0
            )  # The first character wasn't empty. Return to the start of the file.

    def _loadData(self, file, fileExtension: string, argumentName: string, fileReader):
        if file.closed:
            raise ValueError("File is closed.")

        if fileExtension not in file.name.lower():
            raise TypeError(
                "File of type " + fileExtension + " not passed to " + argumentName + "."
            )

        with file:
            try:
                outfile = fileReader(file)
                return outfile
            except EmptyDataError as ed:
                raise EmptyDataError(ed)
            except:
                raise TypeError("Error reading data: " + file.name)

    def getData(self):
        return self._data

    def getColumns(self):
        return self._columns

    def getFeatures(self):
        return self._features

    def getCaching(self):
        return self._caching

    def getDataFileName(self):
        return self._data_file_name

    def getFeatureCustomizations(self):
        return self._feature_customizations
