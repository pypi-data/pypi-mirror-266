from param import List
from rrcgeoviz.JsonCreatorClasses.Blocks.TextBox import TextBox
from rrcgeoviz.JsonCreatorClasses.Sections.BaseSection import BaseSection

from rrcgeoviz.JsonCreatorClasses.Blocks.DownloadButton import DownloadButton


class DownloadSection(BaseSection):
    def header_text(self):
        return "All done? Download the json config file below:"

    def get_all_data(self):
        out_json = {}
        for section in self.list_of_sections:
            if section.dict_or_array() == "dict":
                out_json[section.get_json_section_name()] = {}
                for block in section.get_blocks():
                    [json_name, value] = block.get_value()
                    out_json[section.get_json_section_name()][json_name] = value
            elif section.dict_or_array() == "array":
                out_json[section.get_json_section_name()] = []
                for block in section.get_blocks():
                    [json_name, shouldAdd] = block.get_value()
                    if shouldAdd:
                        out_json[section.get_json_section_name()].append(json_name)

        return out_json

    def __init__(self, list_of_sections) -> None:
        super().__init__()
        self.list_of_sections = list_of_sections

    def generate_blocks(self):
        block = DownloadButton(self.get_all_data)
        return [block]
