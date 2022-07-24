from staze.core.assembler.assembler import Assembler

def get_root_dir() -> str:
    """Return app project root path."""
    return Assembler.instance().get_root_dir()