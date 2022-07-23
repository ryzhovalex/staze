import re
import os
import json
from copy import copy
from dataclasses import dataclass
from typing import Any, TypeVar, Sequence

from warepy import join_paths, load_yaml

from staze.core.app.app_mode_enum import AppModeEnum
from ..assembler.config_extension_enum import ConfigExtensionEnum
from staze.core.model.model import Model
from staze.tools.log import log


class Config(Model):
    """Config config which can be used to load configs to appropriate instance's
    configuration by name."""
    name: str
    source_by_app_mode: dict[AppModeEnum, str]

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
            self, app_mode_enum: AppModeEnum, root_path: str,
            update_with: dict[str, Any] | None = None,
            convert_keys_to_lower: bool = True) -> dict[str, Any]:
        """Parse config config and return configuration dictionary.

        Args:
            app_mode_enum:
                App mode to run appropriate config.
            root_path:
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

        config_by_mode: dict[AppModeEnum, dict] = self._load_config_by_mode()
        res_config = self._update_config_for_mode(config_by_mode, app_mode_enum)

        if res_config:
            self._parse_string_config_values(res_config, root_path)
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
            config_by_mode: dict[AppModeEnum, dict],
            app_mode_enum: AppModeEnum) -> dict:
        """Take config maps for each mode and return result config updated for
        current mode.
        
        E.g., given mode is TEST, so final config will be PROD config updated
        by DEV config and then updated by TEST config (so test keys will
        take priority).
        """ 
        prod_config = copy(config_by_mode[AppModeEnum.PROD])

        if app_mode_enum is AppModeEnum.TEST:
            dev_config = copy(config_by_mode[AppModeEnum.DEV])
            test_config = copy(config_by_mode[AppModeEnum.TEST])
            dev_config.update(test_config)
            prod_config.update(dev_config)
        elif app_mode_enum is AppModeEnum.DEV:
            dev_config = copy(config_by_mode[AppModeEnum.DEV])
            prod_config.update(dev_config)
        else:
            # Prod mode, do nothing extra
            pass
        return prod_config
    
    def _load_config_by_mode(self) -> dict[AppModeEnum, dict]:
        config_by_mode: dict[AppModeEnum, dict] = {}
        for app_mode_enum in AppModeEnum:
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
            self, config: dict[str, Any], root_path: str) -> None:
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

                # Find paths required to be joined to the root path.
                if v[0] == "." and v[1] == "/":
                    config[k] = join_paths(root_path, v)
                else:
                    config[k] = v
