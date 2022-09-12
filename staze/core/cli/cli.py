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
from staze.core.cli.cli_error import CLIError
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

    def execute(
                self,
                args: list[str] | None = None,
                has_to_run_app: bool = True
            ) -> Assembler:
        cli_input: CliInput = self._parse_input(args)

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
                    mode_args=cli_input.mode_args,
                    host=cli_input.host,
                    port=cli_input.port,
                    root_dir=root_dir,
                    build=self.build)

                if has_to_run_app:
                    assembler.run()

                return assembler

    def _parse_input(self, args: list[str] | None = None) -> CliInput:
        if not args:
            args = sys.argv

        check_other_args: bool = True
        mode_kwargs: dict = {}
        mode_kwargs['mode_args'] = []

        match args[1]:
            case 'version':
                if len(args) > 2:
                    raise CLIError(
                        'Mode `version` shouldn\'t be'
                        ' followed by any other arguments')

                mode_enum_class = HelperAppModeEnum
                check_other_args = False 
            case _:
                try:
                    # Find enum where mode assigned
                    mode_enum_class = match_enum_containing_value(
                        args[1], *get_args(AppModeEnumUnion))
                except ValueError:
                    raise CLIError(
                        f'Unrecognized mode: {args[1]}')

        # Create according enum with mode value
        mode_kwargs['mode_enum'] = mode_enum_class(args[1])

        if check_other_args:
            is_previous_flag: bool = False

            for ix, arg in enumerate(args[2:]):
                ix = ix + 2

                match arg:
                    case '-h':
                        if not isinstance(
                                mode_kwargs['mode_enum'], RunAppModeEnum):
                            raise CLIError(
                                'Flag -h applicable only to Run modes:'
                                f' {get_enum_values(RunAppModeEnum)}')
                        elif '-h' in mode_kwargs:
                            raise CLIError('Flag -h has been defined twice')
                        else:
                            try:
                                host = args[ix+1]
                            except KeyError:
                                raise CLIError(
                                    'No host specified for defined flag -h')
                            else:
                                # Pattern from: https://stackoverflow.com/a/36760050
                                validation.validate_re(
                                    host,
                                    r'^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)(\.(?!$)|$)){4}$')
                            mode_kwargs['host'] = host
                            is_previous_flag = True
                    case '-p':
                        if not isinstance(
                                mode_kwargs['mode_enum'], RunAppModeEnum):
                            raise CLIError(
                                'Flag -p applicable only to Run modes:'
                                f' {get_enum_values(RunAppModeEnum)}')
                        elif '-p' in mode_kwargs:
                            raise CLIError('Flag -p has been defined twice')
                        else:
                            try:
                                port = args[ix+1]
                            except KeyError:
                                raise CLIError(
                                    'No port specified for defined flag -p')
                            else:
                                validation.validate_re(
                                    port,
                                    r'^\d+$')
                            mode_kwargs['port'] = port
                            is_previous_flag = True
                    case '-x':
                        # Mode -x applicable to pytest flag and to dev and
                        # prod modes as additional functions executor
                        executable_func_names: list[str] = []

                        if not isinstance(
                                mode_kwargs['mode_enum'], RunAppModeEnum):
                            raise CLIError(
                                'Flag -x can only be used with run modes:'
                                f' {get_enum_values(RunAppModeEnum)}') 

                        # pytest by itself handles -x flag, other cases is up to us
                        if mode_kwargs['mode_enum'] is RunAppModeEnum.TEST:
                            mode_kwargs['mode_args'].append(arg)
                        else:
                            for name in args[ix+1:]:
                                if '-' in name:
                                    break
                                executable_func_names.append(name)

                            if executable_func_names == []:
                                raise CLIError(
                                    'Flag -x for modes prod and dev')

                            mode_kwargs['executable_func_names'].append(
                                executable_func_names)
                            is_previous_flag = True
                    case _:
                        if arg[0] == '-':
                            raise CLIError(f'Unrecognized flag: {arg}')
                        # If value not used by any flag,
                        # e.g. `-h 0.0.0.0 value_without_flag`, raise exception
                        # for run modes
                        elif not is_previous_flag:
                            if mode_enum_class is RunAppModeEnum:
                                if \
                                        mode_kwargs['mode_enum'] \
                                            is not RunAppModeEnum.TEST:
                                    raise CLIError(
                                        'Values without flags is not '
                                        'applicable to mode '
                                        + mode_kwargs['mode_enum'].value
                                    )
                # Write all mode args as it is for extensions read,
                # e.g. for pytest 
                mode_kwargs['mode_args'].append(arg)

        return CliInput(**mode_kwargs)


def main():
    Cli().execute()


if __name__ == "__main__":
    main()
