import panel as pn
from rrcgeoviz.JsonCreatorClasses.Blocks.TextBox import TextBox
from rrcgeoviz.JsonCreatorClasses.Sections.BaseSection import BaseSection

from rrcgeoviz.JsonCreatorClasses.Blocks.Toggle import Toggle

cache_options = [
    {"Descriptive_name": "Cache Results", "json_name": "cache_results"},
    {"Descriptive_name": "Use Cache", "json_name": "use_cache"},
]


class CacheSetter(BaseSection):
    def get_json_section_name(self):
        return "caching"

    def dict_or_array(self):
        return "dict"

    def header_text(self):
        return "Set caching options below."

    def generate_blocks(self):
        blocks = []
        for option in cache_options:
            toggle_thing = Toggle(option["Descriptive_name"], option["json_name"])
            blocks.append(toggle_thing)
        blocks.append(TextBox("cache_location", "~/.geovizcache", "cache_location"))
        return blocks
