from .constants import JOULE_PER_GRAM_CALORIE, JOULE_PER_KILOGRAM_CALORIE
from pyunitconverter.time import SECONDS_PER_HOUR
from pyunitconverter.prefixes import PREFIX_KILO


def joules_to_watt_hour(joules: float) -> float:
    """Convert Joules to Watt Hour

    Args:
        joules (float): The amount of Joules

    Returns:
        float: The amount of Watt Hour
    """
    return joules / SECONDS_PER_HOUR


def watt_hours_to_joules(watt_hours: float) -> float:
    """Convert Watt Hours to Joules

    Args:
        watt_hours (float): The amount of Watt Hours

    Returns:
        float: The amount of Joules
    """
    return watt_hours * SECONDS_PER_HOUR


def joules_to_gram_calories(joules: float) -> float:
    """Convert Joules to Gram Calories

    Args:
        joules (float): The amount of Joules

    Returns:
        float: The amount of Gram Calories
    """
    return joules / JOULE_PER_GRAM_CALORIE


def gram_calories_to_joules(gram_calories: float) -> float:
    """Convert Gram Calories to Joules

    Args:
        gram_calories (float): The amount of Gram Calories

    Returns:
        float: The amount of Joules
    """
    return gram_calories * JOULE_PER_GRAM_CALORIE


def joules_to_kilo_calories(joules: float) -> float:
    """Convert Joules to kilocalories

    Args:
        joules (float): The amount of Joules

    Returns:
        float: The amount of kilocalories
    """
    return joules / JOULE_PER_KILOGRAM_CALORIE


def kilo_calories_to_joules(kilo_calories: float) -> float:
    """Convert kilocalories to Joules

    Args:
        kilo_calories (float): The amount of kilocalories

    Returns:
        float: The amount of Joules
    """
    return kilo_calories * JOULE_PER_KILOGRAM_CALORIE


def gram_calories_to_kilo_calories(gram_calories: float) -> float:
    """Convert Gram Calories to kilocalories

    Args:
        gram_calories (float): The amount of Gram Calories

    Returns:
        float: The amount of kilocalories
    """
    return gram_calories / PREFIX_KILO


def kilo_calories_to_gram_calories(kilo_calories: float) -> float:
    """Convert kilocalories to Gram Calories

    Args:
        kilo_calories (float): The amount of kilocalories

    Returns:
        float: The amount of Gram Calories
    """
    return kilo_calories * PREFIX_KILO


def watt_hour_to_gram_calories(watt_hour: float) -> float:
    """Convert Watt Hour to Gram Calories

    Args:
        watt_hour (float): The amount of Watt Hours

    Returns:
        float: The amount of Gram Calories
    """
    return joules_to_gram_calories(watt_hours_to_joules(watt_hour))


def watt_hour_to_kilo_calories(watt_hour: float) -> float:
    """Convert Watt Hour to kilocalories

    Args:
        watt_hour (float): The amount of Watt Hours

    Returns:
        float: The amount of kilocalories
    """
    return joules_to_kilo_calories(watt_hours_to_joules(watt_hour))


def gram_calories_to_watt_hour(gram_calories: float) -> float:
    """Convert Gram Calories to Watt Hour

    Args:
        gram_calories (float): The amount of Gram Calories

    Returns:
        float: The amount of Watt Hour
    """
    return joules_to_watt_hour(gram_calories_to_joules(gram_calories))


def kilo_calories_to_watt_hour(kilo_calories: float) -> float:
    """Convert Kilocalories to Watt Hour

    Args:
        kilo_calories (float): The amount of Kilocalories

    Returns:
        float: The amount of Watt Hour
    """
    return joules_to_watt_hour(kilo_calories_to_joules(kilo_calories))
