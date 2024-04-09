from rrcgeoviz.JsonCreatorClasses.Blocks.BaseBlock import BaseBlock
import panel as pn


class ArrayTextBox(BaseBlock):
    def get_value(self):
        return [self.json_name, self.stored_value]

    def __init__(self, name, placeholder, json_name) -> None:
        self.stored_value = []
        self.json_name = json_name
        self.name = name
        self.placeholder = placeholder

    def generate_block(self):
        def update_value(textBoxValue):
            if textBoxValue:
                self.stored_value = textBoxValue.split()
            else:
                self.stored_value = []

        column_entry_text = pn.widgets.TextInput(
            name=self.name,
            placeholder=self.placeholder,
        )
        bound_textbox = pn.bind(update_value, textBoxValue=column_entry_text)
        column = pn.Column(column_entry_text, bound_textbox)
        return column
