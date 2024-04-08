from .constants import MS_PER_KMH


def ms_to_kmh(ms: float) -> float:
    """Converts meters per second to kilometers per hour

    Args:
        ms (float): Speed in meters per second

    Returns:
        float: Speed in kilometers per hour
    """
    return ms / MS_PER_KMH


def kmh_to_ms(kmh: float) -> float:
    """Converts kilometers per hour to meters per second

    Args:
        kmh (float): Speed in kilometers per hour

    Returns:
        float: Speed in meters per second
    """
    return kmh * MS_PER_KMH
