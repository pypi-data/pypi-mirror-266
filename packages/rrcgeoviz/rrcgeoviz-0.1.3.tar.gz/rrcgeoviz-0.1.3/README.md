## GeoViz

GeoViz is an Exploratory Data Analysis tool designed to empower data analysts to visualize and interpret spatio-temporal data. It offers a user-friendly, interactive web interface built on Panel, ensuring simplicity and maximal explainability. The software provides visualizations, including 3D geographical coordinates, seasonality analysis, heatmap displays, and categorization/clustering using Natural Language Processing (NLP). With a focus on simplicity and shareability, GeoViz enhances data analysis for a broader audience.

The documentation can be found at our [readthedocs page](https://rincon-geoviz.readthedocs.io/en/latest/index.html).

### Example Usage

First, install GeoViz:

```bash
pip install rrcgeoviz
```

Once done, create an options.json file for your spatio-temporal CSV dataset. Here's a basic example:

```json
{
    "columns": {
        "latitude_column": "latitude",
        "longitude_column": "longitude",
        "time_column": "date",
        "description_column": "description"
    },
    "features": [
        "search_columns",
        "month_year_heatmap",
        "test_option_name",
        "yearly_range",
        "one_year",
        "all_months",
        "one_year_months",
        "threeD",
        "poi_analysis",
        "nlp_bertopics"
    ],
    "caching": {
        "cache_results": false,
        "use_cache": false
    }
}
```

To create an options.json file you can use something like what is shown above or run 
```bash
rrcgeoviz --init
```

Finally, run GeoViz with the following command:

```bash
rrcgeoviz path/to/dataset.csv path/to/options.json
```

A tab should open in your browser with all of the enabled features!

## Brief overview of how it works (for contributers)

When running from the command line, the main() function in src/rrcgeoviz/geoviz_cli.py runs. The options and dataset are stored in an [Arguments object](https://github.com/rrc-byu/ds-capstone-2023-2024/blob/main/src/rrcgeoviz/arguments.py). 

The Arguments object is first passed to the [GeneratedData](https://github.com/rrc-byu/ds-capstone-2023-2024/blob/main/src/rrcgeoviz/GeneratedData.py) class. The GeneratedData class checks whether to pull data from the cache or not. If it needs new data, then it calls any relevant classes in the DATA_GENERATORS array to make it for it to store. The data is then passed back to the Arguments object as the .generateddata attribute.

The Arguments object with the data, options, and generated data is passed to the [GeoVizPanelDashboard class](https://github.com/rrc-byu/ds-capstone-2023-2024/blob/main/src/rrcgeoviz/GeoVizPanelDashboard.py). Here, the data is checked (i.e. it is not null, it's in the correct range, etc.) and then the relevant classes in the ALL_FEATURE_CLASSES  array are called to create the features for GeoViz. These don't make any data, just render what's there into pretty visualizations.

Here's a general flow of how to add new components:
1. If new data is required (e.g. distance to nearest POI) create a new subclass of the [ParentGeneratorClass](https://github.com/rrc-byu/ds-capstone-2023-2024/blob/main/src/rrcgeoviz/datagenerators/ParentDataGenerator.py) in src/rrcgeoviz/datagenerators. Look at [GeneratorExample](https://github.com/rrc-byu/ds-capstone-2023-2024/blob/main/src/rrcgeoviz/datagenerators/GeneratorExample.py) for reference.
2. If a new data generator was made, add it to the DATA_GENERATORS array at the top of the GeneratedData file.
3. Create the panel component as a subclass of [ParentGeovizFeatures](https://github.com/rrc-byu/ds-capstone-2023-2024/blob/main/src/rrcgeoviz/features/ParentGeovizFeature.py) in src/rrcgeoviz/features. Look at other features in the directory for a sense of what they look like.
4. Add the new feature to the ALL_FEATURE_CLASSES array at the top of the GeoVizPanelDashboard file.

That's pretty much it!

