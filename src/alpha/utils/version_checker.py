import sys


def minor_version_gte(minor: int) -> bool:
    """Check is the minor python version is greater then or equal to the minor
    parameter value

    Parameters
    ----------
    minor
        Minor version value

    Returns
    -------
        True if the runtime minor version is greater then or equal to the value
    """
    return sys.version_info.minor >= minor
