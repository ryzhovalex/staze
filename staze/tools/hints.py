from staze.core.cli.cli_db_enum import CLIDbEnum
from staze.core.cli.cli_run_enum import CLIRunEnum
from staze.core.cli.cli_helper_enum import CLIHelperEnum

CLIModeEnumUnion = CLIDbEnum | CLIRunEnum | CLIHelperEnum
