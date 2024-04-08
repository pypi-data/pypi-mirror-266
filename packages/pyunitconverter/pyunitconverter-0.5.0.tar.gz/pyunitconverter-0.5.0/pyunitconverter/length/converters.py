from .constants import CENTIMETER_PER_INCH, METER_PER_INCH, INCH_PER_FEET, FOOT_PER_YARD
from pyunitconverter.prefixes import PREFIX_CENTI, PREFIX_HECTO


def centimeters_to_inches(centimeters: float) -> float:
    """Converts centimeters to inches

    Args:
        centimeters (float): Length in centimeters

    Returns:
        float: length in inches
    """
    return centimeters / CENTIMETER_PER_INCH


def meters_to_inches(meters: float) -> float:
    """Converts meters to inches

    Args:
        meters (float): The numer of meters

    Returns:
        float: The number of inches
    """
    return meters / METER_PER_INCH


def inches_to_centimeters(inches: float) -> float:
    """Converts inches to centimeters

    Args:
        inches (float): Length in inches

    Returns:
        float: Length in centimeters
    """
    return inches * CENTIMETER_PER_INCH


def inches_to_meters(inches: float) -> float:
    """Converts inches to meters

    Args:
        inches (float): Length in inches

    Returns:
        float: Length in meters
    """
    return inches * METER_PER_INCH


def inches_to_feet(inches: float) -> float:
    """Converts inches to feets

    Args:
        inches (float): Length in inches

    Returns:
        float: Length in feet
    """
    return inches / INCH_PER_FEET


def feet_to_inches(feet: float) -> float:
    """Converts feets to inches

    Args:
        feet (float): Length in feet

    Returns:
        float: Length in inches
    """
    return feet * INCH_PER_FEET


def meters_to_feet(meters: float) -> float:
    """Converts meters to feets

    Args:
        meters (float): Length in meters

    Returns:
        float: Length in feet
    """
    return inches_to_feet(meters_to_inches(meters))


def feet_to_meters(feet: float) -> float:
    """Converts feets to meters

    Args:
        feet (float): Length in feet

    Returns:
        float: Length in meters
    """
    return inches_to_meters(feet_to_inches(feet))


def feet_to_centimeters(feet: float) -> float:
    """Converts feet to centimeters

    Args:
        feet (float): Length in feet

    Returns:
        float: Length in centimeters
    """
    return inches_to_centimeters(feet_to_inches(feet))


def centimeters_to_feet(centimeters: float) -> float:
    """Converts centimeters to feet

    Args:
        centimeters (float): Length in centimeters

    Returns:
        float: Length in feet
    """
    return inches_to_feet(centimeters_to_inches(centimeters))


def centimeters_to_meters(centimeters: float) -> float:
    """Converts centimeters to meters

    Args:
        centimeters (float): Length in centimeters

    Returns:
        float: Length in meters
    """
    return centimeters * PREFIX_CENTI


def meters_to_centimeters(meters: float) -> float:
    """Converts meters to centimeters

    Args:
        meters (float): Length in meters

    Returns:
        float: Length in centimeters
    """
    return meters * PREFIX_HECTO


def feet_to_yards(feet: float) -> float:
    """Converts feet to yards

    Args:
        feet (float): Length in feet

    Returns:
        float: Length in yards
    """
    return feet / FOOT_PER_YARD


def yards_to_feet(yards: float) -> float:
    """Converts yards to feet

    Args:
        yards (float): Length in yards

    Returns:
        float: Length in feet
    """
    return yards * FOOT_PER_YARD


def yards_to_meters(yards: float) -> float:
    """Converts yards to meters

    Args:
        yards (float): Length in yards

    Returns:
        float: Length in meters
    """
    return feet_to_meters(yards_to_feet(yards))


def meters_to_yards(meters: float) -> float:
    """Converts meters to yards

    Args:
        meters (float): Length in meters

    Returns:
        float: Length in yards
    """
    return feet_to_yards(meters_to_feet(meters))


def yards_to_inches(yards: float) -> float:
    """Converts yards to inches

    Args:
        yards (float): Length in yards

    Returns:
        float: Length in inches
    """
    return feet_to_inches(yards_to_feet(yards))


def inches_to_yards(inches: float) -> float:
    """Converts inches to yards

    Args:
        inches (float): Length in inches

    Returns:
        float: Length in yards
    """
    return feet_to_yards(inches_to_feet(inches))


def yards_to_centimeters(yards: float) -> float:
    """Converts yards to centimeters

    Args:
        yards (float): Length in yards

    Returns:
        float: Length in centimeters
    """
    return meters_to_centimeters(yards_to_meters(yards))


def centimeters_to_yards(centimeters: float) -> float:
    """Converts centimeters to yards

    Args:
        centimeters (float): Length in centimeters

    Returns:
        float: Length in yards
    """
    return meters_to_yards(centimeters_to_meters(centimeters))
