from staze.core.error.error import Error


class CliError(Error): pass
class RepeatingArgCliError(CliError): pass
class NoMoreArgsCliError(CliError): pass
class RedundantFlagCliError(CliError): pass
class RedundantValueCliError(CliError): pass
class UncompatibleArgsCliError(CliError): pass
