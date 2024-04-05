class ConfigurationReaderOptions:

    def __init__(self):
        self._section_name = "serilog"

    @property
    def section_name(self) -> str:
        return self._section_name

    @section_name.setter
    def section_name(self, value: str):
        self._section_name = value
