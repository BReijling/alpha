"""Secret generator module."""

import secrets


def generate_secret(length: int = 32) -> str:
    """Generate a random secret string.

    Parameters
    ----------
    length : int, optional
        The length of the generated secret, by default 32

    Returns
    -------
    str
        A randomly generated secret string.
    """
    return secrets.token_hex(length).upper()[:length]
