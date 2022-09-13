from staze.core.error.error import Error


class CLIError(Error): pass


class NoMoreArgsCliError(CLIError): pass
