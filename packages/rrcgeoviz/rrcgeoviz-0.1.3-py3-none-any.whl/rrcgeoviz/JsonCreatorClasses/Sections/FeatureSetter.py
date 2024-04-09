from rrcgeoviz.JsonCreatorClasses.Sections.BaseSection import BaseSection

from rrcgeoviz.JsonCreatorClasses.Blocks.ImageCheckbox import ImageCheckBox

option_data = [
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/heatmap.png",
        "description": "Shows a heatmap of the frequency of incidents by year (row) and month (column).",
        "feature": "month_year_heatmap",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/yearly_range.png",
        "description": "Shows the incidents on a world map, with the years shown selected by a range.",
        "feature": "yearly_range",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/one_year_range.png",
        "description": "Same as Year Range Map, but for one year at a time",
        "feature": "one_year",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/all_months.png",
        "description": "Histogram showing the frequency per month across all data points.",
        "feature": "all_months",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/all_months_year.png",
        "description": "Month-to-Month Frequency, but for one year at a time..",
        "feature": "one_year_months",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/threeD.png",
        "description": "A 3D visualization of the data. Latitude, longitude, and time are each a dimension",
        "feature": "threeD",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/poi.png",
        "description": "A point of interest plot",
        "feature": "poi_analysis",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/search.png",
        "description": "Searching DataFrame for Key Term",
        "feature": "search_columns",
    },
    {
        "path": "https://rincon-geoviz.readthedocs.io/en/latest/_images/bert.png",
        "description": "Bertopic Visualizations",
        "feature": "nlp_bertopics",
    },
]


class FeatureSetter(BaseSection):
    def get_json_section_name(self):
        return "features"

    def dict_or_array(self):
        return "array"

    def header_text(self):
        return "Tick the checkboxes above the features you want."

    def generate_blocks(self):
        blocks = []
        for option in option_data:
            blocks.append(
                ImageCheckBox(
                    option["description"],
                    option["path"],
                    option["description"],
                    option["feature"],
                )
            )
        return blocks
