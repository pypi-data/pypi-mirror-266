from typing import Optional

from pyconfig_extension import IConfiguration
from pyserilog import Guard
from pyserilog.core.logging_level_switch import LoggingLevelSwitch


class ResolutionContext:

    def __init__(self, app_configuration: Optional[IConfiguration] = None) -> None:
        self._declaredLevelSwitches: dict[str, LoggingLevelSwitch] = dict()
        self._app_configuration = app_configuration

    def has_app_configuration(self) -> bool:
        return self._app_configuration is not None

    @property
    def app_configuration(self) -> IConfiguration:
        if self._app_configuration is None:
            raise ValueError("AppConfiguration is not available")
        return self._app_configuration

    def add_level_switch(self, level_switch_name: str, level_switch: LoggingLevelSwitch) -> str:
        Guard.against_null(level_switch_name)
        Guard.against_null(level_switch)
        reference_name = self._to_switch_reference(level_switch_name)
        self._declaredLevelSwitches[reference_name] = level_switch
        return reference_name

    def look_up_level_switch_by_name(self, switch_name: str) -> LoggingLevelSwitch:
        if switch_name in self._declaredLevelSwitches:
            return self._declaredLevelSwitches[switch_name]
        raise KeyError(f"No LoggingLevelSwitch has been declared with name \"{switch_name}\"."
                       " You might be missing a section \"LevelSwitches\":{{\"{switchName}\":\"InitialLevel\"}}")

    @staticmethod
    def _to_switch_reference(switch_name: str):
        if switch_name.startswith("$"):
            return switch_name
        else:
            return f"${switch_name}"
