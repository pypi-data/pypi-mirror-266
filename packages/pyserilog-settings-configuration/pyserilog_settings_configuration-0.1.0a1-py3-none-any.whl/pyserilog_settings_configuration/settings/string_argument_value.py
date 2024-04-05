import enum
import types
import typing
from decimal import Decimal

from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.guard import Guard
import importlib

from pyserilog_settings_configuration.settings.configuration_argument_value import IConfigurationArgumentValue
from pyserilog_settings_configuration.settings.resolution_context import ResolutionContext


class StringArgumentValue(IConfigurationArgumentValue):
    def __init__(self, provided_value: str):
        self._provided_value: str = Guard.against_null(provided_value)

    def convert_to(self, klass_type: type, resolution_context: ResolutionContext):
        if klass_type == str:
            return self._provided_value
        if klass_type == LoggingLevelSwitch:
            return resolution_context.look_up_level_switch_by_name(self._provided_value)
        elif typing.get_origin(klass_type) == types.UnionType or typing.get_origin(klass_type) == typing.Union:
            args: tuple = klass_type.__args__
            have_none = len([a for a in args if issubclass(a, types.NoneType)]) != 0
            if have_none and self._provided_value is None or len(self._provided_value) == 0:
                return None
            not_none_types = [a for a in args if not issubclass(a, types.NoneType)]
            if len(not_none_types) != 1:
                raise ValueError()
            klass_type = not_none_types[0]
        if issubclass(klass_type, enum.Enum):
            return self._convert_to_enum(klass_type)

        if self._is_primitive_type(klass_type):
            if klass_type == bool:
                return self._convert_to_boolean()
            return klass_type(self._provided_value)

        if klass_type == type:
            return eval(self._provided_value)

        provided_class: type = self._get_load_module()
        return provided_class()

    def _convert_to_enum(self, klass_type: type):
        key = self._provided_value.lower()
        if len(key) == 0:
            return None
        try:
            key = int(key)
        except ValueError:
            pass
        if isinstance(key, int):
            for mem in klass_type._member_map_:
                if klass_type[mem].value[0] == key:
                    return klass_type[mem]
            raise ValueError(f"invalid enum value  key  {key} for type {klass_type}")

        for mem in klass_type._member_map_:
            if mem.lower() == key:
                return klass_type[mem]
        raise ValueError(f"invalid enum value  key  {key} for type {klass_type}")

    def _get_load_module(self) -> type:
        last_ind = self._provided_value.rindex(".")
        module_name = self._provided_value[:last_ind]
        class_name = self._provided_value[last_ind + 1:]

        module = importlib.import_module(module_name)
        klass: type = getattr(module, class_name)
        return klass

    @staticmethod
    def _is_primitive_type(klass_type):
        return klass_type in (int, float, complex, str, bool, Decimal)

    def _convert_to_boolean(self):
        if self._provided_value in ("False", "false"):
            return False
        elif self._provided_value in ("True", "true"):
            return True
        raise ValueError(f"Invalid value for bool value = '{self._provided_value}'")
