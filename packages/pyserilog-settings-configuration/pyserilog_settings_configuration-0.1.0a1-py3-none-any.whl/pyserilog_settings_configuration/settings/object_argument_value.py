import collections
import types
from collections.abc import Callable

from pyconfig_extension import IConfigurationSection
from pyserilog import Guard, LoggerConfiguration
from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration

from pyserilog_settings_configuration.settings import utils
from pyserilog_settings_configuration.settings.configuration_argument_value import IConfigurationArgumentValue
from pyserilog_settings_configuration.settings.configuration_reader import ConfigurationReader
from pyserilog_settings_configuration.settings.resolution_context import ResolutionContext


class ObjectArgumentValue(IConfigurationArgumentValue):

    def __init__(self, section: IConfigurationSection, packages: list[str] = None):
        self._section: IConfigurationSection = Guard.against_null(section)
        if packages is None:
            packages = []
        self._packages: list[str] = packages

    def convert_to(self, klass_type: type , resolution_context : ResolutionContext):
        if klass_type == IConfigurationSection:
            return self._section
        if self._is_action(klass_type):
            config_type = klass_type.__args__[0]
            config_reader = ConfigurationReader(self._section, packages=self._packages)
            if config_type == LoggerConfiguration:
                return config_reader.configure
            elif config_type == LoggerSinkConfiguration:
                return config_reader.apply_sinks
            elif config_type == LoggerEnrichmentConfiguration:
                return config_reader.apply_enrichment
            else:
                raise ArithmeticError(
                    f"Configuration resolution for Action<{config_type.Name}> "
                    f"parameter type at the path {self._section.path} is not implemented.")
        if utils.is_list(klass_type):
            return self.create_array(klass_type, self._section , resolution_context)

        return self._section.get(klass_type)

    def create_array(self, klass_type: type, section: IConfigurationSection , resolution_context : ResolutionContext) -> list:
        element_type = klass_type.__args__[0]
        config_elements = list(section.get_children())
        res: list = klass_type()
        for element in config_elements:
            argument_value = ConfigurationReader.get_argument_value(element, self._packages)
            value = argument_value.convert_to(element_type , resolution_context)
            res.append(value)
        return res

    @staticmethod
    def _is_action(klass_type: type):
        return hasattr(klass_type , "__origin__") and klass_type.__origin__ == collections.abc.Callable and \
            hasattr(klass_type , "__args__") and len(klass_type.__args__) == 2 and \
            klass_type.__args__[1] == types.NoneType
