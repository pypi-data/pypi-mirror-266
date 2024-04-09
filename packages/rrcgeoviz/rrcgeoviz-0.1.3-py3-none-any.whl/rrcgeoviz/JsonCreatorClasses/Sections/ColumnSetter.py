from rrcgeoviz.JsonCreatorClasses.Blocks.TextBox import TextBox
from rrcgeoviz.JsonCreatorClasses.Sections.BaseSection import BaseSection


class ColumnSetter(BaseSection):
    column_names = [
        {"Descriptive_name": "Time", "json_name": "time_column"},
        {"Descriptive_name": "Longitude", "json_name": "longitude_column"},
        {"Descriptive_name": "Latitude", "json_name": "latitude_column"},
        {
            "Descriptive_name": "Description",
            "json_name": "description_column",
        },
    ]

    def get_json_section_name(self):
        return "columns"

    def dict_or_array(self):
        return "dict"

    def header_text(self):
        return "Input the names of the columns in your csv data for the columns required for the features you want."

    def generate_blocks(self):
        blocks = []
        for column in self.column_names:
            blocks.append(
                TextBox(
                    column["Descriptive_name"] + " column name:",
                    "Enter Column Name here...",
                    column["json_name"],
                )
            )
        return blocks
