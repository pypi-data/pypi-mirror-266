# pylint:disable=undefined-all-variable
""" Expose RealBrowserLocust subclasses at package level """
from .locusts import FirefoxLocust, \
    ChromeLocust, HeadlessChromeLocust

__all__ = [
    'FirefoxLocust',
    'ChromeLocust',
    'HeadlessChromeLocust'
]

__version__ = "0.2"
