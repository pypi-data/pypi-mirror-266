from rrcgeoviz.JsonCreatorClasses.Blocks.TextBox import TextBox
from rrcgeoviz.JsonCreatorClasses.Sections.BaseSection import BaseSection

from rrcgeoviz.JsonCreatorClasses.Blocks.ArrayTextBox import ArrayTextBox


class FeatureCustomizationsSetter(BaseSection):
    def get_json_section_name(self):
        return "features_customizations"

    def dict_or_array(self):
        return "dict"

    def header_text(self):
        return "Optional customizations for features checked above."

    def generate_blocks(self):
        blocks = []
        blocks.append(
            TextBox(
                "Column to filter 'One Year' feature by:",
                "Enter Column Name here...",
                "filter_one_year_column",
            )
        )
        blocks.append(
            ArrayTextBox(
                "Column values to show on hovering over a point on a map:",
                "comma separated column names here...",
                "hover_text_columns",
            )
        )
        return blocks
