import datetime
from rrcgeoviz.datagenerators.ParentDataGenerator import ParentDataGenerator


class GeneratorExample(ParentDataGenerator):
    def getOptionName(self):
        return "cache_tester"

    def generateData(self):
        """An example of making a data generation function.
        Every data generator should take an Arguments object and return the data in a pickle-storable format.
        """
        data = {"type": "is_new"}
        return data
