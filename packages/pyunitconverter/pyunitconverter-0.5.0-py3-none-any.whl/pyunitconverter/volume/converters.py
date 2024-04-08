from .constants import LITER_PER_CUBIC_METER


def cubic_meters_to_liters(cubic_meters):
    """Convert cubic meters to liters

    Args:
        cubic_meters (float): Volume in cubic meters

    Returns:
        float: Volume in liters
    """
    return cubic_meters * LITER_PER_CUBIC_METER


def liters_to_cubic_meters(liters: float) -> float:
    """Convert liters to cubic meters

    Args:
        liters (float): Volume in liters

    Returns:
        float: Volume in cubic meters
    """
    return liters / LITER_PER_CUBIC_METER
