from io import BytesIO
import json
import panel as pn
from rrcgeoviz.JsonCreatorClasses.Blocks.BaseBlock import BaseBlock


class DownloadButton(BaseBlock):
    def __init__(self, get_all_data_func) -> None:
        self.get_all_data = get_all_data_func

    def generate_block(self):
        def generate_json():
            json_content = json.dumps(self.get_all_data(), indent=3).encode()
            json_bytesio = BytesIO(json_content)
            return json_bytesio

        download_json_button = pn.widgets.FileDownload(
            label="Download JSON",
            callback=generate_json,
            filename="options_selected.json",
            button_type="success",
            icon="arrow-bar-to-down",
        )
        return download_json_button
