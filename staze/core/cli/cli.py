import os
import re
import sys
import pytest
from typing import get_args

from warepy import (
    match_enum_containing_value,
    get_enum_values, get_union_enum_values
)
from staze.core.assembler.build import Build
from staze.core.cli.cli_error import CLIError, NoMoreArgsCliError
from staze.core.log import log

from staze import __version__ as staze_version
from staze.core.assembler.assembler import Assembler
from staze.core import validation, parsing
from staze.core.app.app_mode_enum import (
    RunAppModeEnum, DatabaseAppModeEnum, HelperAppModeEnum, AppModeEnumUnion)
from staze.core.cli.cli_input import CliInput


class Cli():
    def __init__(
                self,
                build: Build | None = None,
                root_dir: str | None = None,
            ) -> None:
        self.build = build
        self.root_dir = root_dir
        self.args: list[str] = []

    def execute(
                self,
                args: list[str] | None = None,
                has_to_run_app: bool = True
            ) -> Assembler:
        """Execute args list as cli would do.
        
        Manual way of calling app throuh cli.

        Args:
            args:
                List of each command, e.g. command "staze dev -h 0.0.0.0"
                will look like ['staze', 'dev', '-h', '0.0.0.0'].
            has_to_run_app:
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

        match cli_input.mode_enum:
            case HelperAppModeEnum.VERSION:
                print(f"Staze {staze_version}")
                exit()
            case _:
                root_dir: str
                if self.root_dir:
                    root_dir = self.root_dir
                else:
                    root_dir = os.getcwd()

                # Create and build assembler
                assembler = Assembler(
                    mode_enum=cli_input.mode_enum,
                    mode_args=cli_input.args,
                    host=cli_input.host,
                    port=cli_input.port,
                    root_dir=root_dir,
                    build=self.build)

                if has_to_run_app:
                    assembler.run()

                return assembler

    def _parse_input(self) -> CliInput:

        check_other_args: bool = True
        cli_input_kwargs: dict = {}

        # Useful for third-party extension to read from, e.g. for pytest
        cli_input_kwargs['args'] = self.args

        match self.args[1]:
            case 'version':
                if len(self.args) > 2:
                    raise CLIError(
                        'Mode `version` shouldn\'t be'
                        ' followed by any other arguments')

                mode_enum_class = HelperAppModeEnum
                check_other_args = False 
            case _:
                try:
                    # Find enum where mode assigned
                    mode_enum_class = match_enum_containing_value(
                        self.args[1], *get_args(AppModeEnumUnion))
                except ValueError:
                    raise CLIError(
                        f'Unrecognized mode: {self.args[1]}')

        # Create according enum with mode value
        cli_input_kwargs['mode_enum'] = mode_enum_class(self.args[1])

        if check_other_args:
            # Searching starts from index 2 since first two elements is
            # "staze" and mode keyword
            self._search_args(2, cli_input_kwargs)

        return CliInput(**cli_input_kwargs)

    def _search_args(self, next_index: int, cli_input_kwargs: dict) -> int:
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
                next_index = self._parse_executables(
                    next_index, cli_input_kwargs)
            case _:
                if arg[0] == '-':
                    raise CLIError(f'Unrecognized flag: {arg}')
                # If a value not used by any flag,
                # e.g. `-h 0.0.0.0 value_without_flag`, raise exception
                # for run modes
                elif not is_flag_previous:
                    if mode_enum_class is RunAppModeEnum:
                        if cli_input_kwargs['mode_enum'] \
                                is not RunAppModeEnum.TEST:
                            raise CLIError(
                                'Values without flags is not '
                                'applicable to mode '
                                + cli_input_kwargs['mode_enum'].value
                            )

    def _parse_host(
            self, flag_index: int, cli_input_kwargs: dict
        ) -> int:
        if not isinstance(
                cli_input_kwargs['mode_enum'], RunAppModeEnum):
            raise CLIError(
                'Flag -h applicable only to Run modes:'
                f' {get_enum_values(RunAppModeEnum)}')
        elif '-h' in cli_input_kwargs:
            raise CLIError('Flag -h has been defined twice')
        else:
            try:
                host = self.args[flag_index+1]
            except KeyError:
                raise CLIError(
                    'No host specified for defined flag -h')
            else:
                # Pattern from: https://stackoverflow.com/a/36760050
                validation.validate_re(
                    host,
                    r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$')
            cli_input_kwargs['host'] = host
            return flag_index + 1
                        
    def _parse_port(
            self, flag_index: int, cli_input_kwargs: dict
        ) -> int:
            if not isinstance(
                    cli_input_kwargs['mode_enum'], RunAppModeEnum
                ):
                raise CLIError(
                    'Flag -p applicable only to Run modes:'
                    f' {get_enum_values(RunAppModeEnum)}')
            elif '-p' in cli_input_kwargs:
                raise CLIError('Flag -p has been defined twice')
            else:
                try:
                    port = self.args[flag_index+1]
                except KeyError:
                    raise CLIError(
                        'No port specified for defined flag -p')
                else:
                    validation.validate_re(
                        port,
                        r'^\d+$')
                cli_input_kwargs['port'] = port
                return flag_index + 1

    def _parse_executables(
            self, flag_index: int, cli_input_kwargs: dict
        ) -> int:
        # Mode -x applicable to pytest flag and to dev and
        # prod modes as additional functions executor
        executables: list[str] = []

        if not isinstance(
                cli_input_kwargs['mode_enum'], RunAppModeEnum):
            raise CLIError(
                'Flag -x can only be used with run modes:'
                f' {get_enum_values(RunAppModeEnum)}') 

        # Iterate and add executables until face another flag
        # e.g. in case "... -x exec1 exec2 exec3 -h 0.0.0.0"
        #
        # NOTE:
        #   Pytest is using -x flag too, but anyway such collection is
        #   persormed even in test mode since we anyway need index of next
        #   flag. Assembler will take the rest of the separation logic.
        #
        for name in self.args[flag_index+1:]:
            if '-' in name:
                break
            executables.append(name)

        if executables == []:
            raise CLIError(
                'No executables specified for flag -x')

        cli_input_kwargs['executables'].append(
            executables)
        # Return index of the next flag counting amount of added cli
        # arguments
        return flag_index + len(executables) + 1


def main():
    """Entrypoint for setup.py"""
    Cli().execute()


if __name__ == "__main__":
    main()
