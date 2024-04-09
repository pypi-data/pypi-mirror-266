from rrcgeoviz.JsonCreatorClasses.Blocks.BaseBlock import BaseBlock
import panel as pn


class ImageCheckBox(BaseBlock):
    def get_value(self):
        return [self.json_name, self.stored_value]

    def __init__(self, name, image_url, image_description, json_name) -> None:
        self.stored_value = None
        self.name = name
        self.image_url = image_url
        self.json_name = json_name
        self.image_description = image_description

    def generate_block(self):
        def update_value(boxTicked):
            if boxTicked:
                self.stored_value = True

        checkbox = pn.widgets.Checkbox(name=self.name)
        binded_checkbox = pn.bind(update_value, boxTicked=checkbox)
        image = pn.pane.Image(self.image_url, width=500, caption=self.image_description)
        column = pn.Column(checkbox, binded_checkbox, image)
        return column
