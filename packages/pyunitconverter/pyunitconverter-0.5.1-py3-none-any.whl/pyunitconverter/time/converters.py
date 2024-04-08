from .constants import SECONDS_PER_MINUTE, SECONDS_PER_HOUR, SECONDS_PER_DAY, SECONDS_PER_WEEK
from .constants import MINUTES_PER_HOUR, MINUTES_PER_DAY, MINUTES_PER_WEEK
from .constants import HOURS_PER_DAY, HOURS_PER_WEEK
from .constants import DAYS_PER_WEEK


def seconds_to_minutes(seconds: float) -> float:
    """Converts seconds to minutes

    Args:
        seconds (float): Number of seconds

    Returns:
        float: Number of minutes
    """
    return seconds / SECONDS_PER_MINUTE


def seconds_to_hours(seconds: float) -> float:
    """Converts seconds to hours.

    Args:
        seconds (float): Number of seconds.

    Returns:
        float: Number of hours.
    """
    return seconds / SECONDS_PER_HOUR


def seconds_to_days(seconds: float) -> float:
    """Converts seconds to days.

    Args:
        seconds (float): Number of seconds.

    Returns:
        float: Number of days.
    """
    return seconds / SECONDS_PER_DAY


def seconds_to_weeks(seconds: float) -> float:
    """Converts seconds to weeks.

    Args:
        seconds (float): Number of seconds.

    Returns:
        float: Number of weeks.
    """
    return seconds / SECONDS_PER_WEEK


def minutes_to_seconds(minutes: float) -> float:
    """Converts minutes to seconds.

    Args:
        minutes (float): Number of minutes.

    Returns:
        float: Number of seconds.
    """
    return minutes * SECONDS_PER_MINUTE


def hours_to_seconds(hours: float) -> float:
    """Converts hours to seconds.

    Args:
        hours (float): Number of hours.

    Returns:
        float: Number of seconds.
    """
    return hours * SECONDS_PER_HOUR


def days_to_seconds(days: float) -> float:
    """Converts days to seconds.

    Args:
        days (float): Number of days.

    Returns:
        float: Number of seconds.
    """
    return days * SECONDS_PER_DAY


def weeks_to_seconds(weeks: float) -> float:
    """Converts weeks to seconds.

    Args:
        weeks (float): Number of weeks.

    Returns:
        float: Number of seconds.
    """
    return weeks * SECONDS_PER_WEEK


def minutes_to_hours(minutes: float) -> float:
    """Converts minutes to hours.

    Args:
        minutes (float): Number of minutes.

    Returns:
        float: Number of hours.
    """
    return minutes * MINUTES_PER_HOUR


def minutes_to_days(minutes: float) -> float:
    """Converts minutes to day.

    Args:
        minutes (float): Number of minutes.

    Returns:
        float: Number of day.
    """
    return minutes * MINUTES_PER_DAY


def minutes_to_weeks(minutes: float) -> float:
    """Converts minutes to weeks.

    Args:
        minutes (float): Number of minutes.

    Returns:
        float: Number of weeks.
    """
    return minutes * MINUTES_PER_WEEK


def hours_to_days(hours: float) -> float:
    """Converts hours to day.

    Args:
        hours (float): Number of hours.

    Returns:
        float: Number of day.
    """
    return hours * HOURS_PER_DAY


def hours_to_weeks(hours: float) -> float:
    """Converts hours to weeks.

    Args:
        hours (float): Number of hours.

    Returns:
        float: Number of weeks.
    """
    return hours * HOURS_PER_WEEK


def days_to_weeks(days: float) -> float:
    """Converts days to weeks.

    Args:
        days (float): Number of days.

    Returns:
        float: Number of weeks.
    """
    return days * DAYS_PER_WEEK


def weeks_to_days(weeks: float) -> float:
    """Converts weeks to days.

    Args:
        weeks (float): Number of weeks.

    Returns:
        float: Number of days.
    """
    return weeks / DAYS_PER_WEEK


def week_to_hours(weeks: float) -> float:
    """Converts weeks to hours.

    Args:
        weeks (float): Number of weeks.

    Returns:
        float: Number of hours.
    """
    return weeks * HOURS_PER_WEEK


def days_to_minutes(days: float) -> float:
    """Converts days to minutes.

    Args:
        days (float): Number of days.

    Returns:
        float: Number of minutes.
    """
    return days * MINUTES_PER_DAY


def days_to_hours(days: float) -> float:
    """Converts days to hours.

    Args:
        days (float): Number of days.

    Returns:
        float: Number of hours.
    """
    return days * HOURS_PER_DAY


def hours_to_minutes(hours: float) -> float:
    """Converts hours to minutes

    Args:
        hours (float): Numbers of hours

    Returns:
        float: Number of minutes
    """
    return hours * MINUTES_PER_HOUR


def weeks_to_minutes(weeks: float) -> float:
    """Converts weeks to minutes

    Args:
        weeks (float): Number of weeks

    Returns:
        float: Number of minutes
    """
    return weeks * MINUTES_PER_WEEK
