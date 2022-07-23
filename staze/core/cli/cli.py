import os
import re
import sys
import pytest
from typing import get_args

from warepy import (
    format_message, join_paths, match_enum_containing_value,
    get_enum_values, get_union_enum_values
)
from staze.core.cli.cli_error import CLIError
from staze.tools.log import log
from dotenv import load_dotenv

from staze import __version__ as staze_version
from staze.core.assembler.assembler import Assembler
from staze.core import validation, parsing
from staze.tools.hints import CLIModeEnumUnion
from .cli_run_enum import CLIRunEnum
from .cli_database_enum import CLIDatabaseEnum
from .cli_helper_enum import CLIHelperEnum
from staze.core.cli.cli_input_ie import CLIInputIe


def main() -> None:
    # Environs should be loaded from app's root directory
    load_dotenv(os.path.join(os.getcwd(), '.env'))

    args: CLIInputIe = _parse_input()

    match args.mode_enum:
        case CLIHelperEnum.VERSION:
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


def _parse_input() -> CLIInputIe:
    args: list[str] = sys.argv
    check_other_args: bool = True

    ie_kwargs: dict = {}
    ie_kwargs['mode_args'] = []


    match args[1]:
        case 'version':
            if len(args) > 2:
                raise CLIError(
                    'Mode `version` shouldn\'t be'
                    ' followed by any other arguments')

            ie_kwargs['mode_enum'] = CLIHelperEnum.VERSION
            check_other_args = False 
        case _:
            try:
                # Find enum where mode assigned
                mode_enum_class = match_enum_containing_value(
                    args[1], *get_args(CLIModeEnumUnion))
            except ValueError:
                raise CLIError(
                    f'Unrecognized mode: {args[1]}')
            else:
                # Create according enum with mode value
                ie_kwargs['mode_enum'] = mode_enum_class(args[1])

    if check_other_args:
        # Traverse other args
        for ix, arg in enumerate(args[2:]):
            ix = ix + 2

            match arg:
                case '-h':
                    if not isinstance(ie_kwargs['mode_enum'], CLIRunEnum):
                        raise CLIError(
                            'Flag -h applicable only to Run modes:'
                            f' {get_enum_values(CLIRunEnum)}')
                    elif '-h' in ie_kwargs:
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
                            ie_kwargs['host'] = host
                case '-p':
                    if not isinstance(ie_kwargs['mode_enum'], CLIRunEnum):
                        raise CLIError(
                            'Flag -p applicable only to Run modes:'
                            f' {get_enum_values(CLIRunEnum)}')
                    elif '-p' in ie_kwargs:
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
                            ie_kwargs['port'] = port
                case _:
                    # In all other cases, write results to mode_args as it is,
                    # this is required, e.g. in pytest as well as in all other
                    # plugins and custom commands
                    ie_kwargs['mode_args'].append(arg)

    return CLIInputIe(**ie_kwargs)


if __name__ == "__main__":
    main()
