import importlib
import inspect
import pkgutil
import types
from collections.abc import Callable
from importlib.resources import Package
from inspect import Parameter
from typing import Optional

from pyconfig_extension import IConfigurationSection
from pyconfig_extension.abstracts.iconfiguration_root import IConfigurationRoot
from pyserilog import LoggerConfiguration
from pyserilog.configuration.logger_audit_sink_configuration import LoggerAuditSinkConfiguration
from pyserilog.configuration.logger_destructuring_configuration import LoggerDestructuringConfiguration
from pyserilog.configuration.logger_enrichment_configuration import LoggerEnrichmentConfiguration
from pyserilog.configuration.logger_filter_configuration import LoggerFilterConfiguration
from pyserilog.configuration.logger_minimum_level_configuration import LoggerMinimumLevelConfiguration
from pyserilog.configuration.logger_sink_configuration import LoggerSinkConfiguration
from pyserilog.core.logging_level_switch import LoggingLevelSwitch
from pyserilog.events.log_event_level import LogEventLevel
from pyserilog.settings.key_value_paies.surrogate_configuration_methods import SurrogateConfigurationMethods

from .configuration_argument_value import IConfigurationArgumentValue
from .iconfiguration_reader import IConfigurationReader
from pyconfig_extension.abstracts.iconfiguration import IConfiguration

from .resolution_context import ResolutionContext
from .string_argument_value import StringArgumentValue

import re

switch_name_regex = re.compile("^\${0,1}[A-Za-z]+[A-Za-z0-9]*$")


class ConfigurationReader(IConfigurationReader):
    def __init__(self, config_section: IConfiguration, configuration: IConfiguration = None,
                 packages: list[str] = None):
        self._config_section = config_section
        if packages is not None:
            self._packages = packages
        else:
            self._packages: list[str] = self.load_configuration_packages(config_section)
        if isinstance(configuration, IConfigurationRoot):
            self._configuration_root: IConfigurationRoot = configuration
        else:
            self._configuration_root: IConfigurationRoot = None
        self._resolution_context = ResolutionContext(configuration)

    def apply_sinks(self, logger_sink_configuration: LoggerSinkConfiguration) -> None:
        method_calls = self.get_call_methods(self._config_section)
        methods = self._find_sink_configuration_methods(self._packages)
        self.call_configuration_methods(method_calls, methods, logger_sink_configuration)

    def apply_enrichment(self, logger_enrichment_configuration: LoggerEnrichmentConfiguration) -> None:
        method_calls = self.get_call_methods(self._config_section)
        methods = self._find_event_enricher_configuration_methods(self._packages)
        self.call_configuration_methods(method_calls, methods, logger_enrichment_configuration)

    def configure(self, logger_configuration: LoggerConfiguration) -> None:
        self._process_level_switch_declarations()

        self._apply_minimum_level(logger_configuration)
        self._apply_enrichment(logger_configuration)
        self._apply_filter(logger_configuration)
        self._apply_destructuring(logger_configuration)
        self._apply_sinks(logger_configuration)
        self._apply_audit_sinks(logger_configuration)

    def _process_level_switch_declarations(self):
        level_switch_directive = self._config_section.get_section("level_switches")
        for level_switch_declaration in level_switch_directive.get_children():
            switch_name = level_switch_declaration.key
            switch_initial_value = level_switch_declaration.value
            if not self.is_valid_switch_name(switch_name):
                raise ValueError(f"({switch_name})  is not a valid name for a Level Switch declaration."
                                 f" The first character of the name must be a letter or"
                                 f" '$' sign, like \"LevelSwitches\" : {{\"$switchName\" : \"InitialLevel\"}}")

            if switch_initial_value is None or len(switch_initial_value) == 0:
                new_switch = LoggingLevelSwitch()
            else:
                initial_level = self._parse_log_event_level(switch_initial_value)
                new_switch = LoggingLevelSwitch(initial_level)

            reference_name = self._resolution_context.add_level_switch(switch_name, new_switch)

    # def _process_filter_switch_declarations(self):
    #     filter_switch_directive = self._config_section.get_section("filter_switches")
    #
    #     for filter_switch_declaration in filter_switch_directive.get_children():

    def _apply_minimum_level(self, logger_configuration: LoggerConfiguration):
        minimum_level_directive = self._config_section.get_section("minimum_level")

        def get_default_min_level_directive() -> IConfigurationSection:
            default_level_directive = minimum_level_directive.get_section("default")
            if self._configuration_root is not None and \
                    minimum_level_directive.value is not None and \
                    default_level_directive.value is not None:
                providers = reversed(self._configuration_root.providers)
                for provider in providers:
                    if provider.try_get(minimum_level_directive.path)[0]:
                        return self._configuration_root.get_section(minimum_level_directive.path)
                    if provider.try_get(default_level_directive.path)[0]:
                        return self._configuration_root.get_section(default_level_directive.path)

            if minimum_level_directive.value is not None:
                return minimum_level_directive
            else:
                return minimum_level_directive.get_section("default")
            pass

        def applyMinimumLevelConfiguration(
                directive: IConfigurationSection,
                apply_config_action: Callable[[LoggerMinimumLevelConfiguration, LoggingLevelSwitch], types.NoneType]
        ):
            minimum_level = self._parse_log_event_level(directive.value)
            level_switch = LoggingLevelSwitch(minimum_level)
            apply_config_action(logger_configuration.minimum_level, level_switch)

        default_min_level_directive = get_default_min_level_directive()
        if default_min_level_directive.value is not None:
            applyMinimumLevelConfiguration(default_min_level_directive, lambda x, y: x.controlled_by(y))

        min_level_controlled_by_directive = minimum_level_directive.get_section("controlled_by")
        if min_level_controlled_by_directive.value is not None:
            global_minimum_level_switch = self._resolution_context.look_up_level_switch_by_name(min_level_controlled_by_directive.value)
            logger_configuration.minimum_level.controlled_by(global_minimum_level_switch)

        for override_directive in minimum_level_directive.get_section("override").get_children():
            override_prefix = override_directive.key
            override_level_or_switch = override_directive.value
            if self._can_parse_log_event_level(override_level_or_switch):
                applyMinimumLevelConfiguration(override_directive, lambda x, y: x.override(override_prefix, y))
            elif override_level_or_switch is not None and len(override_level_or_switch) > 0:
                override_switch = self._resolution_context.look_up_level_switch_by_name(override_level_or_switch)
                logger_configuration.minimum_level.override(override_prefix, override_switch)

    def _apply_enrichment(self, logger_configuration: LoggerConfiguration):
        enrich_directive = self._config_section.get_section("enrich")
        if len(enrich_directive.get_children()) > 0:
            method_calls = self.get_call_methods(enrich_directive)
            methods = self._find_event_enricher_configuration_methods(self._packages)
            self.call_configuration_methods(method_calls, methods, logger_configuration.enrich)

        properties_directive = self._config_section.get_section("properties")
        prop_children = properties_directive.get_children()
        if len(prop_children) > 0:
            for child in prop_children:
                logger_configuration.enrich.with_property(child.key, child.value)
        pass

    def _apply_sinks(self, logger_configuration: LoggerConfiguration):
        write_to_directive = self._config_section.get_section("write_to")
        children = write_to_directive.get_children()
        if len(children) > 0:
            method_calls = self.get_call_methods(write_to_directive)
            methods = self._find_sink_configuration_methods(self._packages)
            self.call_configuration_methods(method_calls, methods, logger_configuration.write_to)

    def _apply_filter(self, logger_configuration: LoggerConfiguration):
        write_to_directive = self._config_section.get_section("filter")
        children = write_to_directive.get_children()
        if len(children) > 0:
            method_calls = self.get_call_methods(write_to_directive)
            methods = self._find_filter_configuration_methods(self._packages)
            self.call_configuration_methods(method_calls, methods, logger_configuration.filter)

    def _apply_destructuring(self, logger_configuration: LoggerConfiguration):
        write_to_directive = self._config_section.get_section("destructure")
        children = write_to_directive.get_children()
        if len(children) > 0:
            method_calls = self.get_call_methods(write_to_directive)
            methods = self._find_destructure_configuration_methods(self._packages)
            self.call_configuration_methods(method_calls, methods, logger_configuration.destructure)

    def _apply_audit_sinks(self, logger_configuration: LoggerConfiguration):
        audit_to_directive = self._config_section.get_section("audit_to")
        if len(audit_to_directive.get_children()) > 0:
            method_calls = self.get_call_methods(audit_to_directive)
            methods = self._find_audit_sink_configuration_methods(self._packages)
            self.call_configuration_methods(method_calls, methods, logger_configuration.audit_to)

    def get_call_methods(self, configuration: IConfiguration) \
            -> dict[str, list[dict[str, IConfigurationArgumentValue]]]:
        result = dict()
        children = configuration.get_children()

        for child in children:
            if child.value is not None:
                key = child.value
                value = dict()
            else:
                key = self._get_section_name(child)
                args_child = child.get_section("args").get_children()
                value = {ar.key: self.get_argument_value(ar, self._packages) for ar in args_child}
            if key not in result:
                result[key] = list()
            result[key].append(value)

        return result

    @staticmethod
    def select_configuration_method(candidate_methods: list[staticmethod],
                                    name: str,
                                    supplied_argument_names: list[str]) -> staticmethod | None:
        def is_valid_method(method: staticmethod) -> bool:
            signature = inspect.signature(method)
            parameters = signature.parameters
            if len(parameters) == 0:
                return False
            index = 0
            for param_name in parameters:
                if index == 0:
                    index += 1
                    continue
                index += 1
                param = parameters[param_name]
                if not (param_name in supplied_argument_names \
                        or ConfigurationReader.has_implicit_value_when_not_specified(param)):
                    return False
            return True

        methods = [m for m in candidate_methods if (m.__name__ == name and is_valid_method(m))]

        def sort_key(method: staticmethod):
            params = inspect.signature(method).parameters.values()
            count = len([f for f in params if f.name in supplied_argument_names])
            str_count = len([f for f in params if f.annotation == str])
            return count, str_count

        methods.sort(key=lambda m: sort_key(m), reverse=True)
        if len(methods) > 0:
            return methods[0]
        return None

    def call_configuration_methods(self, methods: dict[str, list[dict[str, IConfigurationArgumentValue]]],
                                   configuration_methods: list[staticmethod],
                                   receiver
                                   ):
        for method_name in methods:
            infos = methods[method_name]
            for info in infos:
                keys = list(info.keys())
                method_info: staticmethod = ConfigurationReader.select_configuration_method(configuration_methods,
                                                                                            method_name, keys)
                if method_info is not None:
                    signature = inspect.signature(method_info)
                    args = dict()
                    parameters = list(signature.parameters.values())
                    args[parameters[0].name] = receiver
                    for param in parameters:
                        if param.name in info:
                            value = info[param.name].convert_to(param.annotation, self._resolution_context)
                            args[param.name] = value
                        else:
                            value = self._get_implicit_value_for_not_specified_key(param, method_info.__name__)
                            if value is not None:
                                args[param.name] = value

                    method_info(**args)
                else:
                    print(f"Method '{method_name}' not found")

        pass

    def _get_implicit_value_for_not_specified_key(self, parameter: Parameter, method_to_invoke_name: str):
        if parameter.annotation == IConfiguration:
            if self._resolution_context.has_app_configuration():
                return self._resolution_context.app_configuration
            if parameter.default != inspect.Parameter.empty:
                return parameter.default
            raise ValueError("Trying to invoke a configuration method accepting a `IConfiguration` argument. "
                             f"This is not supported when only a `IConfigSection` has been provided. (method '{method_to_invoke_name}')")

    @staticmethod
    def load_configuration_packages(section: IConfiguration) -> list[str]:
        packages: set[str] = set()
        packages.add("pyserilog")
        import_section = section.get_section("imports")
        if len(import_section.get_children()) > 0:
            names = [f.value for f in import_section.get_children()]
            for name in names:
                if name is None or len(name) == 0:
                    raise ValueError(f"A zero-length or whitespace assembly name was supplied to a"
                                     f" {import_section.path} configuration statement.")
                packages.add(name)
        return list(packages)

    @staticmethod
    def _find_sink_configuration_methods(configuration_packages: list[str]):
        founds = ConfigurationReader._find_configuration_extension_methods(configuration_packages,
                                                                           LoggerSinkConfiguration)
        founds.update(SurrogateConfigurationMethods.write_to)
        return list(founds)

    @staticmethod
    def _find_filter_configuration_methods(configuration_packages: list[str]):
        founds = ConfigurationReader._find_configuration_extension_methods(configuration_packages,
                                                                           LoggerFilterConfiguration)
        founds.update(SurrogateConfigurationMethods.filter_to)
        return list(founds)

    @staticmethod
    def _find_destructure_configuration_methods(configuration_packages: list[str]):
        founds = ConfigurationReader._find_configuration_extension_methods(configuration_packages,
                                                                           LoggerDestructuringConfiguration)
        return list(founds)

    @staticmethod
    def _find_event_enricher_configuration_methods(configuration_packages: list[str]):
        founds = ConfigurationReader._find_configuration_extension_methods(configuration_packages,
                                                                           LoggerEnrichmentConfiguration)
        return list(founds)

    @staticmethod
    def _find_audit_sink_configuration_methods(configuration_packages: list[str]):
        founds = ConfigurationReader._find_configuration_extension_methods(configuration_packages,
                                                                           LoggerAuditSinkConfiguration)
        return list(founds)

    @staticmethod
    def _find_configuration_extension_methods(configuration_packages: list[str], config_type: type) -> set[staticmethod]:
        result: set[staticmethod] = set()
        for pkg in configuration_packages:
            path = importlib.import_module(pkg).__path__
            modules = [name for t, name, c in list(pkgutil.walk_packages(path, prefix=pkg + "."))]
            for module_name in modules:
                module = importlib.import_module(f"{module_name}")
                members = [obj for name, obj in inspect.getmembers(module) if
                           (not name.startswith("__") and inspect.isclass(obj))
                           ]
                for obj in members:
                    methods = [b for _, b in inspect.getmembers_static(obj) if
                               (hasattr(b, "__name__") and
                                (not b.__name__.startswith("__")) and
                                isinstance(b, staticmethod))]
                    for m in methods:
                        parameters = list(inspect.signature(m).parameters.values())
                        if len(parameters) > 0 and parameters[0].annotation == config_type:
                            result.add(m)
        return result

    @staticmethod
    def has_implicit_value_when_not_specified(param: Parameter) -> bool:
        return param.default != inspect.Parameter.empty or param.annotation == IConfiguration

    @staticmethod
    def is_valid_switch_name(switch_name: str) -> bool:
        match_reg = switch_name_regex.match(switch_name)
        return bool(match_reg)

    @staticmethod
    def _get_section_name(section: IConfigurationSection):
        name = section.get_section("name")
        if name.value is None:
            raise ValueError(f"The configuration value {name.path} has no 'name' element.");

        return name.value

    @staticmethod
    def get_argument_value(argument_section: IConfigurationSection,
                           packages: list[str]) -> IConfigurationArgumentValue:

        # Reject configurations where an element has both scalar and complex
        # values as a result of reading multiple configuration sources.
        if argument_section.value is not None and len(argument_section.get_children()) > 0:
            raise ValueError(f"The value for the argument '{argument_section.path}' is assigned different value " +
                             "types in more than one configuration source. Ensure all configurations consistently " +
                             "use either a scalar (int, string, boolean) or a complex (array, section, list, " +
                             "POCO, etc.) type for this argument value.")

        if argument_section.value is not None:
            return StringArgumentValue(argument_section.value)
        else:
            from .object_argument_value import ObjectArgumentValue
            return ObjectArgumentValue(argument_section, packages=packages)

    @staticmethod
    def _parse_log_event_level(value: str) -> LogEventLevel:
        res = [k for k in LogEventLevel if k.name.lower() == value.lower()]
        if len(res) == 1:
            return res[0]
        raise ValueError(f"The value {value} is not a valid Serilog level.")

    @staticmethod
    def _can_parse_log_event_level(log_event_level: str) -> bool:
        try:
            ConfigurationReader._parse_log_event_level(log_event_level)
            return True
        except:
            return False
