import os
from os import listdir
from os.path import isfile, join
from pathlib import Path
import pickle
import warnings
from rrcgeoviz.datagenerators.GeneratorBertopic import GeneratorBertopic
from rrcgeoviz.datagenerators.ParentDataGenerator import ParentDataGenerator
from rrcgeoviz.datagenerators.GeneratorExample import GeneratorExample
from rrcgeoviz.datagenerators.GeneratorPOI import GeneratorPOI
from rrcgeoviz.arguments import Arguments

DATA_GENERATORS = [GeneratorExample, GeneratorBertopic, GeneratorPOI]
os.environ["TOKENIZERS_PARALLELISM"] = "true"


class GeneratedData:
    def __init__(self, arguments: Arguments):
        self.arguments = arguments

        self.location = self._setLocation()
        self.should_cache = self._setShouldCache()
        self.use_cache = self._setUseCache()
        self.cache_files = self._setCacheFiles()

        self.data_dict = {}
        self.fresh_data_dict = {}

        if self.use_cache and self.should_cache:
            raise TypeError("Can't cache results and use cache at the same time.")

        # check if each feature was requested to generate
        for generatorType in DATA_GENERATORS:
            generator: ParentDataGenerator = generatorType(self.arguments)
            feature = generator.getOptionName()
            if feature in arguments.getFeatures():  # if it's in the list
                if self.shouldMakeFresh(feature):  # if need fresh data gen
                    self.callDataGeneration(generator)  # actually generate the data
                else:
                    self.loadData(featureName=feature)  # read cache

        # if should cache, store the data
        if self.should_cache:
            self.cacheGeneratedData(fresh_data_dict=self.fresh_data_dict)

        # TODO: make any calls to generate_data get the data through the parameter data_dict
        self.data_dict.update(self.fresh_data_dict)

    def getData(self):
        return self.data_dict

    # arguments.generated_data.data_dict["generator_bertopic"]
    def _setLocation(self):
        if "cache_location" in self.arguments.getCaching():
            return self.arguments.getCaching()["cache_location"]
        else:
            return os.path.join(os.path.curdir, ".geovizcache")

    def _setShouldCache(self):
        if (
            "cache_results" in self.arguments.getCaching()
            and self.arguments.getCaching()["cache_results"] == True
        ):
            Path(self.location).mkdir(parents=True, exist_ok=True)
            return True
        else:
            return False

    def _setUseCache(self):
        if (
            "use_cache" in self.arguments.getCaching()
            and self.arguments.getCaching()["use_cache"] == True
        ):
            return True
        else:
            return False

    def _setCacheFiles(self):
        if self.use_cache:
            return [f for f in listdir(self.location) if isfile(join(self.location, f))]
        else:
            return []

    def loadData(self, featureName):
        read_path = self.location + "/" + str(featureName) + ".pkl"
        with open(read_path, "rb") as pickle_file:
            result = pickle.load(pickle_file)
        self.data_dict[featureName] = result

    def callDataGeneration(self, generator: ParentDataGenerator):
        result = generator.generateData()
        self.data_dict[generator.getOptionName()] = result
        self.fresh_data_dict[generator.getOptionName()] = result

    def shouldMakeFresh(self, featureName):
        if self.use_cache == False:
            return True
        if str(featureName) + ".pkl" not in self.cache_files:
            warnings.warn(
                "use_cache was set, but not all of the required cache data was found. Generating new data for:"
                + str(featureName),
                UserWarning,
            )
            return True
        return False

    def cacheGeneratedData(self, fresh_data_dict: dict):
        print("caching data...")
        for key, value in fresh_data_dict.items():
            filepath = self.location + "/" + str(key) + ".pkl"
            file = open(filepath, "wb")
            pickle.dump(value, file)
            file.close()
