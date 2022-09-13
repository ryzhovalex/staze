from staze.core.error.error import Error


class CliError(Error): pass
class NoMoreArgsCliError(CliError): pass
class VersionCliError(CliError): pass
