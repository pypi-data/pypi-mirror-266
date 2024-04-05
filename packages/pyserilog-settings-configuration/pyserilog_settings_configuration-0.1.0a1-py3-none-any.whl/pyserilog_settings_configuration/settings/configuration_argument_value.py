from abc import ABC, abstractmethod
import importlib

from pyserilog_settings_configuration.settings.resolution_context import ResolutionContext


class IConfigurationArgumentValue(ABC):

    @abstractmethod
    def convert_to(self, klass_type: type, resolution_context : ResolutionContext):
        pass
