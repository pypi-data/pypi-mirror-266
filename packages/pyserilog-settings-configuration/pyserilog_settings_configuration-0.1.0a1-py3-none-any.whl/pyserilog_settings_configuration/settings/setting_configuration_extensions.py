import types
from collections.abc import Callable

from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.events.level_alias import LevelAlias
from pyserilog.events.log_event_level import LogEventLevel


class SettingConfigurationExtensions:

    @staticmethod
    def at_level(
            logger_enrichment_configuration: LoggerEnrichmentConfiguration,
            configure_enricher: Callable[[LoggerEnrichmentConfiguration], types.NoneType],
            enrich_from_level: LogEventLevel = LevelAlias.minimum,
            level_switch: LoggingLevelSwitch = None
    ):
        if level_switch is not None:
            return logger_enrichment_configuration.at_level(level_switch, configure_enricher)
        return logger_enrichment_configuration.at_level(enrich_from_level, configure_enricher)
