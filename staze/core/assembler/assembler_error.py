from staze.core.error.error import Error


class AssemblerError(Error): pass

class ExecAssemblerError(AssemblerError): pass
class NoExecutableWithSuchNameExecAssemblerError(ExecAssemblerError): pass
class NoDefinedExecutablesExecAssemblerError(ExecAssemblerError): pass
