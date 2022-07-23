from staze.core.assembler.assembler import Assembler


def get_mode() -> str:
    """Return app mode string representation."""
    return Assembler.instance().get_mode_enum().value