from .constants import KELVIN_TO_CELSIUS


def celsius_to_fahrenheit(celsius_temp: float) -> float:
    """Returns the Fahrenheit temperature from a Celsius value

    Args:
        celsius_temp (float): Celsius temperature

    Returns:
        float: Fahrenheit temperature
    """
    if celsius_temp < -273.15:
        raise ValueError("Celsius temperature must be greeter -273.15")

    return celsius_temp * 9 / 5 + 32


def celsius_to_kelvin(celsius_temp: float) -> float:
    """Returns the Kelvin temperature from a Celsius value

    Args:
        celsius_temp (float): Celsius temperature

    Returns:
        float: Kelvin temperature
    """
    if celsius_temp < -273.15:
        raise ValueError("Celsius temperature must be greeter -273.15")

    return celsius_temp + KELVIN_TO_CELSIUS


def fahrenheit_to_celsius(fahrenheit_temp: float) -> float:
    """Returns the Celsius temperature from a Fahrenheit value

    Args:
        fahrenheit_temp (float): Fahrenheit temperature

    Returns:
        float: Celsius temperature
    """
    if fahrenheit_temp < -459.67:
        raise ValueError("Fahrenheit temperature must be greeter -459.67")

    return (fahrenheit_temp - 32) * 5 / 9


def fahrenheit_to_kelvin(fahrenheit_temp: float) -> float:
    """Returns the Kelvin temperature from a Fahrenheit value

    Args:
        fahrenheit_temp (float): Fahrenheit temperature

    Returns:
        float: Kelvin temperature
    """
    if fahrenheit_temp < -459.67:
        raise ValueError("Fahrenheit temperature must be greeter -459.67")

    return celsius_to_kelvin(fahrenheit_to_celsius(fahrenheit_temp))


def kelvin_to_celsius(kelvin_temp: float) -> float:
    """Returns the Celsius temperature from a Kelvin value

    Args:
        kelvin_temp (float): Kelvin temperature

    Returns:
        float: Celsius temperature
    """
    if kelvin_temp < 0:
        raise ValueError("Kelvin temperature must be greater than 0")

    return kelvin_temp - KELVIN_TO_CELSIUS


def kelvin_to_fahrenheit(kelvin_temp: float) -> float:
    """Returns the Fahrenheit temperature from a Kelvin value

    Args:
        kelvin_temp (float): Kelvin temperature

    Returns:
        float: Fahrenheit temperature
    """
    if kelvin_temp < 0:
        raise ValueError("Kelvin temperature must be greater than 0")

    return celsius_to_fahrenheit(kelvin_to_celsius(kelvin_temp))
