"""Small cross-platform console helpers used by executable modules."""
import sys


def configure_utf8() -> None:
    """Use UTF-8 when the active stdout stream supports reconfiguration."""
    reconfigure = getattr(sys.stdout, 'reconfigure', None)
    if callable(reconfigure):
        reconfigure(encoding='utf-8')
