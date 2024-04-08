from .constants import OUNCE_PER_POUND, OUNCE_PER_KILOGRAM


def ounces_to_pounds(ounces: float) -> float:
    """Converts ounces to pounds

    Args:
        ounces (float): Mass in ounces

    Returns:
        float: Mass in pounds
    """
    return ounces / OUNCE_PER_POUND


def pounds_to_ounces(pounds: float) -> float:
    """Converts pounds to ounces

    Args:
        pounds (float): Mass in pounds

    Returns:
        float: Mass in ounces
    """
    return pounds * OUNCE_PER_POUND


def kilograms_to_ounces(kilograms: float) -> float:
    """Converts kilograms to ounces

    Args:
        kilograms (float): Mass in kilograms

    Returns:
        float: Mass in ounces
    """
    return kilograms * OUNCE_PER_KILOGRAM


def ounces_to_kilograms(ounces: float) -> float:
    """Converts ounces to kilograms

    Args:
        ounces (float): Mass in ounces

    Returns:
        float: Mass in kilograms
    """
    return ounces / OUNCE_PER_KILOGRAM


def kilograms_to_pounds(kilograms: float) -> float:
    """Converts kilograms to pounds

    Args:
        kilograms (float): Mass in kilograms

    Returns:
        float: Mass in pounds
    """
    return ounces_to_pounds(kilograms_to_ounces(kilograms))


def pounds_to_kilograms(pounds: float) -> float:
    """Converts pounds to kilograms

    Args:
        pounds (float): Mass in pounds

    Returns:
        float: Mass in kilograms
    """
    return ounces_to_kilograms(pounds_to_ounces(pounds))
