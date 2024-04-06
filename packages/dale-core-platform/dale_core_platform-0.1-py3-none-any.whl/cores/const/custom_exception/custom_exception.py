class DriverSelError(Exception):
    """custom class for Selenium Driver handling

    Args:
        Exception (_type_): _description_
    """
    pass


class DriverAppError(Exception):
    """custom class for Appium Driver handling

    Args:
        Exception (_type_): _description_
    """
    pass


class RequestError(Exception):
    """custom class for Request handling

    Args:
        Exception (_type_): _description_
    """
    pass


class RequestTimeout(Exception):
    """custom class for Request timeout

    Args:
        Exception (_type_): _description_
    """
    pass


class DbError(Exception):
    """custom class for Daatabase handling

    Args:
        Exception (_type_): _description_
    """
    pass
