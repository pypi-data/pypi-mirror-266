from requests.exceptions import HTTPError, Timeout, ConnectionError, RequestException, MissingSchema
from functools import wraps
from selenium.common import StaleElementReferenceException, NoSuchElementException, TimeoutException, ElementClickInterceptedException


from cores.const.custom_exception import RequestError, DriverSelError, RequestTimeout
from ..utils.common.logger_util import logger


def handle_exception(f):
    """Decorator to handle exception while requesting resource

    Args:
        f (_type_): _description_

    Raises:
        Timeout: _description_
        HTTPError: _description_
        ConnectionError: _description_
        RequestException: _description_
        AttributeError: _description_
        MissingSchema: _description_
        Exception: _description_

    Returns:
        _type_: _description_
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Timeout as timeout_err:
            raise RequestTimeout(f'Request timeout {timeout_err}')
        except HTTPError as http_err:
            raise RequestError(f'HTTP error {http_err}')
        except ConnectionError as con_err:
            raise RequestTimeout(f'Connection error {con_err}')
        except RequestException as request_err:
            raise RequestError(f'Request error {request_err}')
        except AttributeError as attribute_err:
            raise RequestError(f'Attribute error {attribute_err}')
        except MissingSchema as schema_err:
            raise RequestError(f'Schema error {schema_err}')
    return decorated


def handle_selenium_exception(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        locator = kwargs.get('locator')

        try:
            return f(*args, **kwargs)
        except (StaleElementReferenceException, NoSuchElementException, TimeoutException,
                ElementClickInterceptedException) as e:
            logger.warn(DriverSelError(
                "An exception of type " + type(e).__name__ +
                " occurred. With Element -: " +
                "locator: (" + locator['by'] + ", " + locator['value'] + ")"
            ))
            if f.__name__ == 'find_element':
                return None
            elif f.__name__ in ['find_elements', 'find_elements_inside_element']:
                return []
            else:
                raise e
        finally:
            pass
    return wrapper
