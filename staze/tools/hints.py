from staze.core.cli.cli_database_enum import CLIDatabaseEnum
from staze.core.cli.cli_run_enum import CLIRunEnum
from staze.core.cli.cli_helper_enum import CLIHelperEnum

CLIModeEnumUnion = CLIDatabaseEnum | CLIRunEnum | CLIHelperEnum
