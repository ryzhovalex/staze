import os
import re
import sys
from typing import get_args

import pytest
from staze.core import parsing, validation
from staze.core.app.app_mode_enum import (AppModeEnumUnion,
                                          DatabaseAppModeEnum,
                                          HelperAppModeEnum, RunAppModeEnum)
from staze.core.assembler.assembler import Assembler
from staze.core.assembler.build import Build
from staze.core.cli.cli_error import (CliError, NoMoreArgsCliError,
                                      RedundantFlagCliError,
                                      RedundantValueCliError, RepeatingArgCliError, UncompatibleArgsCliError)
from staze.core.cli.cli_input import CliInput
from staze.core.log.log import log
from warepy import (get_enum_values, get_union_enum_values,
                    match_enum_containing_value)


class Cli():
    def __init__(
                self,
                build: Build | None = None,
                root_dir: str | None = None,
            ) -> None:
        self.build = build
        self.root_dir = root_dir
        self.args: list[str] = []

        # Whether to check following flags or values. If false, raise error if
        # following flag/value is occured
        self._has_to_check_following_flags: bool = True
        self._has_to_check_following_values: bool = True

    def execute(
                self,
                args: list[str] | None = None,
                has_to_run_assembler: bool = True,
                _has_to_recreate_migrations: bool = False,
                _is_self_test: bool = False
            ) -> Assembler:
        """Execute args list as cli would do.
        
        Manual way of calling app throuh cli.

        Args:
            args:
                List of each command, e.g. command "staze dev -h 0.0.0.0"
                will look like ['staze', 'dev', '-h', '0.0.0.0'].
            has_to_run_assembler:
                Whether app should be run right after configuration. Defaults
                to True.
        """
        if args:
            self.args = args
        else:
            # FIXME:
            #   Debug module calls.
            #
            #   Probably call via module, like "python -m staze dev ..." will
            #   broke this logic, since we expect "staze" as first argument.
            self.args = sys.argv

        cli_input: CliInput = self._parse_input()

        root_dir: str
        if self.root_dir:
            root_dir = self.root_dir
        else:
            root_dir = os.getcwd()

        # Create and build assembler
        assembler = Assembler(
            mode_enum=cli_input.mode_enum,
            cli_args=cli_input.args,
            host=cli_input.host,
            port=cli_input.port,
            root_dir=root_dir,
            build=self.build, 
            executables_to_execute=cli_input.executables_to_execute,
            _has_to_recreate_migrations=_has_to_recreate_migrations,
            _is_self_test=_is_self_test
        )

        if has_to_run_assembler:
            assembler.run()

        return assembler

    def _parse_input(self) -> CliInput:
        cli_input_kwargs: dict = {}

        # Useful for third-party extension to read from, e.g. for pytest
        cli_input_kwargs['args'] = self.args
        cli_input_kwargs['executables_to_execute'] = []

        match self.args[1]:
            case 'version':
                ModeEnumClass = HelperAppModeEnum
                self._has_to_check_following_flags = False 
                self._has_to_check_following_values = False
            case 'exec':
                ModeEnumClass = HelperAppModeEnum
                self._has_to_check_following_flags = False 
                self._has_to_check_following_values = True
            case _:
                try:
                    # Find enum where mode assigned
                    ModeEnumClass = match_enum_containing_value(
                        self.args[1], *get_args(AppModeEnumUnion))
                except ValueError:
                    raise CliError(
                        f'Unrecognized mode: {self.args[1]}')

        # Create according enum with mode value
        cli_input_kwargs['mode_enum'] = ModeEnumClass(self.args[1])

        # Searching starts from index 2 since first two elements is
        # "staze" and mode keyword. Searching starts in any case, even if it's
        # not required (e.g. mode "version" already picked) to find possible
        # mistakes and raise error for that
        try:
            self._search_args(2, cli_input_kwargs)
        except NoMoreArgsCliError:
            pass

        return CliInput(**cli_input_kwargs)

    def _search_args(self, next_index: int, cli_input_kwargs: dict) -> None:
        try:
            arg = self.args[next_index]
        except IndexError:
            raise NoMoreArgsCliError()

        # Every function "parser" returns an integer "index" means index to
        # continue from. This is required because of arguments following
        # one flag, to be read only from one parser.
        # In other words, "index" is often denotes next flag, which may be
        # applicable to next type of parser.
        match arg:
            case '-h':
                next_index = self._parse_host(next_index, cli_input_kwargs)
            case '-p':
                next_index = self._parse_port(next_index, cli_input_kwargs)
            case '-x':
                next_index = self._parse_executables_to_execute(
                    next_index, cli_input_kwargs)
            case _:
                if arg[0] == '-' and not self._has_to_check_following_flags:
                    raise RedundantFlagCliError()
                elif arg[0] != '-' and not self._has_to_check_following_values:
                    raise RedundantValueCliError()
                # i.e. value which wanted to be saved, e.g. for "exec" mode
                # which doesn't accept flags, but only values
                else:
                    if cli_input_kwargs['mode_enum'] is HelperAppModeEnum.EXEC:
                        cli_input_kwargs['executables_to_execute'].append(
                            arg
                        )
                        next_index += 1
                    else:
                        raise CliError(
                            'Additional cli values is requested, but no'
                            ' mode logic is presented to handle them'
                            f' (occured for argument {arg})'
                        )

        self._search_args(next_index, cli_input_kwargs)

    def _parse_host(
            self, flag_index: int, cli_input_kwargs: dict
        ) -> int:
        try:
            cli_input_kwargs['host']
        except KeyError:
            pass
        else:
            raise RepeatingArgCliError('Flag -h has been defined twice')
        
        try:
            host = self.args[flag_index+1]
        except KeyError:
            raise CliError(
                'No host specified for defined flag -h')
        else:
            # Pattern from: https://stackoverflow.com/a/36760050
            validation.validate_re(
                host,
                r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$')
        cli_input_kwargs['host'] = host
        return flag_index + 1 + 1
                        
    def _parse_port(
            self, flag_index: int, cli_input_kwargs: dict
        ) -> int:
            try:
                cli_input_kwargs['port']
            except KeyError:
                pass
            else:
                raise RepeatingArgCliError('Flag -p has been defined twice')

            try:
                port = self.args[flag_index+1]
            except KeyError:
                raise CliError(
                    'No port specified for defined flag -p')
            else:
                validation.validate_re(
                    port,
                    r'^\d+$')
            cli_input_kwargs['port'] = port
            return flag_index + 1 + 1

    def _parse_executables_to_execute(
            self, flag_index: int, cli_input_kwargs: dict
        ) -> int:
        # Mode -x applicable to pytest flag and to dev and
        # prod modes as additional functions executor
        executables_to_execute: list[str] = []

        if len(cli_input_kwargs['executables_to_execute']) != 0:
            raise RepeatingArgCliError('Flag -x has been defined twice')

        if type(cli_input_kwargs['mode_enum']) is not RunAppModeEnum:
            raise UncompatibleArgsCliError(
                'Flag -x is only applicable to run app modes')

        # Iterate and add executables until face another flag
        # e.g. in case "staze dev -x exec1 exec2 exec3 -h 0.0.0.0"
        #
        # NOTE:
        #   Pytest is using -x flag too, but anyway such collection is
        #   persormed even in test mode since we anyway need index of next
        #   flag. Assembler will take the rest of the separation logic.
        #
        for name in self.args[flag_index+1:]:
            if '-' in name:
                break
            executables_to_execute.append(name)

        if cli_input_kwargs['mode_enum'] is not RunAppModeEnum.TEST:
            if executables_to_execute == []:
                raise CliError(
                    'No executables specified for flag -x')
            cli_input_kwargs['executables_to_execute'] = executables_to_execute
        # Return index of the next flag counting amount of added cli
        # arguments
        return flag_index + len(executables_to_execute) + 1


def main():
    """Entrypoint for setup.py"""
    Cli().execute()


if __name__ == "__main__":
    main()
