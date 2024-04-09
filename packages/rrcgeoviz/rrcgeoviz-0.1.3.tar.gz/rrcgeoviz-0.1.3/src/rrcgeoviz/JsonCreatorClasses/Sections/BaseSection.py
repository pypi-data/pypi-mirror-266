from typing import List
from rrcgeoviz.JsonCreatorClasses.Blocks.BaseBlock import BaseBlock
import panel as pn


class BaseSection:
    blocks: List[BaseBlock] = []

    def header_text(self):
        raise NotImplementedError("Add header text here")

    def generate_blocks(self):
        raise NotImplementedError("Return array of panel components")

    def get_json_section_name(self):
        raise NotImplementedError("Return JSON section name here")

    def dict_or_array(self):
        raise NotImplementedError("return either string 'dict' or 'array")

    def get_block_values(self):
        out = []
        for block in self.blocks:
            out.append(block.get_value())

    def generate_section(self):
        self.blocks = self.generate_blocks()

        output = pn.Column()
        output.append(
            pn.Row(
                pn.layout.HSpacer(),
                pn.widgets.StaticText(
                    value=self.header_text(),
                ),
                pn.layout.HSpacer(),
            )
        )
        for block in self.blocks:
            row = pn.Row(
                pn.layout.HSpacer(), block.generate_block(), pn.layout.HSpacer()
            )
            output.append(row)
        return output

    def __init__(self) -> None:
        self.blocks = None

    def get_blocks(self):
        if self.blocks is None:
            self.blocks = self.generate_blocks()
            return self.blocks
        else:
            return self.blocks
