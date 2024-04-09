class BaseBlock:
    def get_value(self):
        raise NotImplementedError("Returns [json_name, value]")

    def generate_block(self):
        raise NotImplementedError("return a Panel component")
