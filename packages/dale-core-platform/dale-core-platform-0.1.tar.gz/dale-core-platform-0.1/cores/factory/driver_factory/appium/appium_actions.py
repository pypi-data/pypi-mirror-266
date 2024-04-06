import re

from appium.webdriver.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from cores.const.common import StoreConst, TimeConst
from cores.const.common.key_codes_const import KeycodeConst
from cores.const.custom_exception import DriverAppError
from cores.factory.driver_factory import MobileDriver
from cores.utils.common import GetUtil


class AppiumActions(MobileDriver):
    def __init__(self, driver, timeout: int = MobileDriver.TIMEOUT):
        super().__init__(driver)
        self._wait_time_default = timeout
        self._locators = GetUtil.scenario_get(StoreConst.LOCATORS)

    def find_element(self, locator_name: str, timeout: int = None, **kwargs):
        locator = self.modify_locator(locators=self._locators, name=locator_name, value=kwargs.get('value'))
        ele: WebElement = WebDriverWait(self.driver, timeout if timeout else self._wait_time_default).until(
            EC.presence_of_element_located((locator['by'], locator['value'])))
        return ele

    def click_gesture(self, locator_name: str = None, timeout: int = None, **kwargs):
        if kwargs.get('coordinates'):
            if isinstance(kwargs.get('coordinates'), dict):
                self.driver.execute_script('mobile: clickGesture',
                                           {'x': kwargs.get('coordinates').get('x'),
                                            'y': kwargs.get('coordinates').get('y')})
            else:
                raise DriverAppError(f'Invalid coordinates format')
        else:
            self.driver.execute_script('mobile: clickGesture',
                                       {'elementId': self.find_element(locator_name=locator_name,
                                                                       timeout=timeout,
                                                                       value=kwargs.get('value')).id})

    def long_click_gesture(self, locator_name: str, timeout: int = None, **kwargs):
        self.driver.execute_script('mobile: longClickGesture',
                                   {'elementId': self.find_element(locator_name=locator_name,
                                                                   timeout=timeout, value=kwargs.get('value')).id,
                                    'duration': 1000})

    def get_bounds_info(self, locator_name: str, timeout: int = None, **kwargs):
        """
        Returns: left, top, right, bottom
        """
        # bound: [left, top][right, bottom]
        bounds = self.find_element(locator_name=locator_name,
                                   timeout=timeout, value=kwargs.get('value')).get_attribute(name="bounds")
        # handle str
        r = re.findall(r'\[([^]]+)\]', bounds)
        out = []
        for l in r:
            out.extend(i for i in l.split(','))
        left, top, right, bottom = out
        return float(left), float(top), float(right), float(bottom)

    def is_element_enabled(self, locator_name: str, timeout: int = None, **kwargs):
        return self.find_element(locator_name=locator_name,
                                 timeout=timeout, value=kwargs.get('value')).is_enabled()

    def press_keycode_on_android(self, value: str, locator_name: str, timeout: int = None, **kwargs):
        """
        Sends a keycode to the device.
        Android only. Possible keycodes can be found
        """
        for _ in range(TimeConst.Retry.DEFAULT):
            if self.driver.is_keyboard_shown():
                break
            self.find_element(locator_name=locator_name,
                              timeout=timeout, value=kwargs.get('value')).click()
            self.click_gesture(locator_name=locator_name, timeout=timeout, value=kwargs.get('value'))
        for keycode in value:
            self.driver.press_keycode(keycode=KeycodeConst.key[keycode])
