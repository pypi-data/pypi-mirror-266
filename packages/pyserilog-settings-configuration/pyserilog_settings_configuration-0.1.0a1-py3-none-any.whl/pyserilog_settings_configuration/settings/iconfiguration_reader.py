from abc import ABC, abstractmethod

from pyserilog.configuration.ilogger_settings import ILoggerSettings
from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration


class IConfigurationReader(ILoggerSettings, ABC):

    @abstractmethod
    def apply_sinks(self, logger_sink_configuration: LoggerSinkConfiguration) -> None:
        pass

    @abstractmethod
    def apply_enrichment(self, logger_enrichment_configuration: LoggerEnrichmentConfiguration) -> None:
        pass
