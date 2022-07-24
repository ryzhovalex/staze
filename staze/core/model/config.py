import re
import os
import json
from copy import copy
from dataclasses import dataclass
from typing import Any, TypeVar, Sequence

from warepy import load_yaml, get_enum_values

from staze.core.app.app_mode_enum import RunAppModeEnum
from ..assembler.config_extension_enum import ConfigExtensionEnum
from staze.core.model.model import Model
from staze.core.log import log


class Config(Model):
    """Config config which can be used to load configs to appropriate instance's
    configuration by name."""
    name: str
    source_by_app_mode: dict[RunAppModeEnum, str]

    @staticmethod
    def find_by_name(name: str, configs: list['Config']) -> 'Config':
        """Traverse through given list of configs and return first one with
        specified name.
        
        Raise:
            ValueError: 
                No config with given name found.
        """
        for config in configs:
            if config.name == name:
                return config

        raise ValueError(
            "No config found with given name: {}", name)

    def parse(
            self, app_mode_enum: RunAppModeEnum, root_dir: str,
            update_with: dict[str, Any] | None = None,
            convert_keys_to_lower: bool = True) -> dict[str, Any]:
        """Parse config config and return configuration dictionary.

        Args:
            app_mode_enum:
                App mode to run appropriate config.
            root_dir:
                Path to join config config source with.
            update_with (optional):
                Dictionary to update config config mapping with.
                Defaults to None.
            convert_keys_to_lower (optional):
                If true, all keys from origin mapping and mapping from
                `update_with` will be converted to upper case.
        
        Raise:
            ValueError:
                If given config config's source has unrecognized extension.
        """
        res_config: dict[str, Any] = {}

        config_by_mode: dict[RunAppModeEnum, dict] = self._load_config_by_mode()
        res_config = self._update_config_for_mode(config_by_mode, app_mode_enum)

        if res_config:
            self._parse_string_config_values(res_config, root_dir)
        else:
            res_config = {}

        # Update given config with extra dictionary if this dictionary given
        # and not empty.
        if update_with:
            res_config.update(update_with)

        if convert_keys_to_lower:
            temp_config = {}
            for k, v in res_config.items():
                temp_config[k.lower()] = v
            res_config = temp_config

        return res_config

    def _update_config_for_mode(
            self,
            config_by_mode: dict[RunAppModeEnum, dict],
            app_mode_enum: RunAppModeEnum) -> dict:
        """Take config maps for each mode and return result config updated for
        current mode.
        
        E.g., given mode is TEST, so final config will be PROD config updated
        by DEV config and then updated by TEST config (so test keys will
        take priority).
        """ 
        prod_config = copy(config_by_mode[RunAppModeEnum.PROD])

        if app_mode_enum is RunAppModeEnum.TEST:
            dev_config = copy(config_by_mode[RunAppModeEnum.DEV])
            test_config = copy(config_by_mode[RunAppModeEnum.TEST])
            dev_config.update(test_config)
            prod_config.update(dev_config)
        elif app_mode_enum is RunAppModeEnum.DEV:
            dev_config = copy(config_by_mode[RunAppModeEnum.DEV])
            prod_config.update(dev_config)
        else:
            # Prod mode, do nothing extra
            pass
        return prod_config
    
    def _load_config_by_mode(self) -> dict[RunAppModeEnum, dict]:
        config_by_mode: dict[RunAppModeEnum, dict] = {}
        for app_mode_enum in RunAppModeEnum:
            try:
                source = self.source_by_app_mode[app_mode_enum]
            except KeyError:
                # No source for such mode
                config_by_mode[app_mode_enum] = {}
                continue
            source_extension = source[source.rfind(".")+1:]
            config_by_mode[app_mode_enum] = self._load_config_from_file(
                source_extension_enum=ConfigExtensionEnum(source_extension),
                source=source)
        return config_by_mode
    
    def _load_config_from_file(
            self,
            source_extension_enum: ConfigExtensionEnum, source: str) -> dict:
        # Fetch extension and load config from file.
        match source_extension_enum:
            case ConfigExtensionEnum.JSON:
                with open(source, "r") as config_file:
                    config = json.load(config_file)
            case ConfigExtensionEnum.YAML:
                config = load_yaml(source)
                if config is None:
                    raise NotImplementedError(self.name)
            case _:
                raise ValueError("Unrecognized config config source's extension")
        return config
    
    def _parse_string_config_values(
            self, config: dict[str, Any], root_dir: str) -> None:
        for k, v in config.items():
            if type(v) == str:
                # Find environs to be requested
                # Exclude escaped curly brace like `\{not_environ}`
                # Note that environs matching \w+ pattern only supported
                # 
                # Negative look behind used:
                # https://stackoverflow.com/a/3926546
                envs: list[str] = re.findall(r"(?<!\\)\{\w+\}", v)
                if envs:
                    for env in [
                                x.replace("{", "").replace("}", "")
                                for x in envs
                            ]:
                        env = env.strip()
                        real_env_value = os.getenv(env.strip())
                        if real_env_value is None:
                            raise ValueError(
                                f"Environ {env} specified in field"
                                f" {self.name}.{k} was not found")
                        else:
                            v = v.replace("{" + f"{env}" + "}", real_env_value)

                # Look for escaped curly braces and normalize them.
                v = v.replace(r"\{", "{").replace(r"\}", "}")

                config[k] = v

    @staticmethod
    def find_config_files(
            config_path: str) -> dict[str, dict[RunAppModeEnum, str]]:
        """Accept path to config dir and return dict describing all paths to
        configs for all app modes per service name.
        
        Return example:
        ```python
        {
            "custom_service_name": {
                AppModeEnum.PROD: "./some/path",
                AppModeEnum.DEV: "./some/path",
                AppModeEnum.TEST: "./some/path"
            }
        }
        ```
        """
        source_map_by_name = {} 
        for filename in os.listdir(config_path):
            # Pick files only under config_dir.
            if os.path.isfile(os.path.join(config_path, filename)):
                parts = filename.split(".")
                file_path = os.path.join(config_path, filename)

                if len(parts) == 1:
                    # Skip files without extension.
                    continue
                # Check if file has supported extension.
                elif len(parts) == 2:
                    # Config name shouldn't contain dots and thus we can grab
                    # it right here.
                    config_name = parts[0]
                    if parts[1] in get_enum_values(ConfigExtensionEnum):
                        # Add file without app mode automatically to
                        # `prod`.
                        if config_name not in source_map_by_name:
                            source_map_by_name[config_name] = dict()
                        source_map_by_name[config_name][
                            RunAppModeEnum.PROD] = file_path
                    else:
                        # Skip files with unsupported extension.
                        continue
                elif len(parts) == 3:
                    # Config name shouldn't contain dots and thus we can grab
                    # it right here.
                    config_name = parts[0]
                    if parts[1] in get_enum_values(RunAppModeEnum) \
                            and parts[2] in get_enum_values(
                                ConfigExtensionEnum):
                        # File has both normal extension and defined
                        # app mode.
                        if config_name not in source_map_by_name:
                            source_map_by_name[config_name] = dict()
                        source_map_by_name[config_name][
                            RunAppModeEnum(parts[1])] = file_path
                    else:
                        # Unrecognized app mode or extension,
                        # maybe raise warning?
                        continue
                else:
                    # Skip files with names containing dots, e.g.
                    # "dummy.new.prod.yaml".
                    continue
        return source_map_by_name
