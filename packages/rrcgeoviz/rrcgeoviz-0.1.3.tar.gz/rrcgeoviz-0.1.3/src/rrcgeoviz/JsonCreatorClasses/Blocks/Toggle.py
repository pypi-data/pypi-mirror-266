from rrcgeoviz.JsonCreatorClasses.Blocks.BaseBlock import BaseBlock
import panel as pn


class Toggle(BaseBlock):
    def get_value(self):
        return [self.json_name, self.stored_value]

    def __init__(self, name, json_name) -> None:
        self.stored_value = None
        self.json_name = json_name
        self.name = name

    def generate_block(self):
        def update_value(toggleValue):
            if toggleValue:
                self.stored_value = toggleValue
            else:
                self.stored_value = False

        toggle = pn.widgets.Switch(name=self.name, value=False)
        bound_toggle = pn.bind(update_value, toggleValue=toggle)
        column = pn.Row(
            pn.widgets.StaticText(value=self.name + ": "), toggle, bound_toggle
        )
        return column
