from charts._base import MODES


def value_mode_toggle(page_key: str = None, default: str = None) -> str:
    """The Numbers / Percentage switch has been removed: the dashboard now
    shows Numbers only. Kept as a tiny function that renders nothing and
    returns "Numbers", so every chart function (which still accepts a `mode`
    argument) keeps working unchanged."""
    return MODES[0]  # "Numbers"
