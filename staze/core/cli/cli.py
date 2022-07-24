import os
import re
import sys
import pytest
from typing import get_args

from warepy import (
    match_enum_containing_value,
    get_enum_values, get_union_enum_values
)
from staze.core.cli.cli_error import CLIError
from staze.core.log import log

from staze import __version__ as staze_version
from staze.core.assembler.assembler import Assembler
from staze.core import validation, parsing
from staze.core.app.app_mode_enum import (
    RunAppModeEnum, DatabaseAppModeEnum, HelperAppModeEnum, AppModeEnumUnion)
from staze.core.cli.cli_input import CliInput


def main() -> None:
    args: CliInput = _parse_input()

    match args.mode_enum:
        case HelperAppModeEnum.VERSION:
            print(f"Staze {staze_version}")
            exit()
        case _:
            # Create and build assembler
            assembler = Assembler(
                mode_enum=args.mode_enum,
                mode_args=args.mode_args,
                host=args.host,
                port=int(args.port))

            assembler.run()


def _parse_input() -> CliInput:
    args: list[str] = sys.argv
    check_other_args: bool = True

    model_kwargs: dict = {}
    model_kwargs['mode_args'] = []


    match args[1]:
        case 'version':
            if len(args) > 2:
                raise CLIError(
                    'Mode `version` shouldn\'t be'
                    ' followed by any other arguments')

            model_kwargs['mode_enum'] = HelperAppModeEnum.VERSION
            check_other_args = False 
        case _:
            try:
                # Find enum where mode assigned
                mode_enum_class = match_enum_containing_value(
                    args[1], *get_args(AppModeEnumUnion))
            except ValueError:
                raise CLIError(
                    f'Unrecognized mode: {args[1]}')
            else:
                # Create according enum with mode value
                model_kwargs['mode_enum'] = mode_enum_class(args[1])

    if check_other_args:
        # Traverse other args
        for ix, arg in enumerate(args[2:]):
            ix = ix + 2

            match arg:
                case '-h':
                    if not isinstance(model_kwargs['mode_enum'], RunAppModeEnum):
                        raise CLIError(
                            'Flag -h applicable only to Run modes:'
                            f' {get_enum_values(RunAppModeEnum)}')
                    elif '-h' in model_kwargs:
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
                        model_kwargs['host'] = host
                case '-p':
                    if not isinstance(model_kwargs['mode_enum'], RunAppModeEnum):
                        raise CLIError(
                            'Flag -p applicable only to Run modes:'
                            f' {get_enum_values(RunAppModeEnum)}')
                    elif '-p' in model_kwargs:
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
                        model_kwargs['port'] = port
                case _:
                    # In all other cases, write results to mode_args as it is,
                    # this is required, e.g. in pytest as well as in all other
                    # plugins and custom commands
                    model_kwargs['mode_args'].append(arg)

    return CliInput(**model_kwargs)


if __name__ == "__main__":
    main()
