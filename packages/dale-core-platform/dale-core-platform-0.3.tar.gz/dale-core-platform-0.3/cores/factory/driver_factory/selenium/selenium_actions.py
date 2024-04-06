import random

from appium.webdriver.webdriver import WebDriver
from selenium.common import StaleElementReferenceException, NoSuchElementException, ElementClickInterceptedException, \
    TimeoutException
from selenium.webdriver import ActionChains, Keys
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from cores.const.common import StoreConst
from cores.decorators import handle_selenium_exception
from cores.utils.common import TimeUtil, GetUtil, logger
from ..selenium.selenium_driver import SeleniumDriver


class SeleniumActions(SeleniumDriver):

    def __init__(self, driver, timeout: int = SeleniumDriver.TIMEOUT):
        super().__init__(driver)
        self._driver: WebDriver = driver
        self._wait_time_default = timeout
        self._locators = GetUtil.scenario_get(StoreConst.LOCATORS)

    # @handle_selenium_exception
    # def find_element_pom(self, element: dict, timeout: int = None, **kwargs):
    #     ele = WebDriverWait(self._driver, timeout if timeout else self.TIMEOUT).until(
    #         EC.presence_of_element_located(mapping[locator=]))
    #     return ele

    @handle_selenium_exception
    def find_element(self, locator_name: str, timeout: int = None, **kwargs):
        locator = self.modify_pom_locator(
            locators=self._locators, name=locator_name, value=kwargs.get('value'))
        ele: WebElement = WebDriverWait(self._driver, timeout if timeout else self._wait_time_default).until(
            EC.presence_of_element_located((locator['by'], locator['value'])))
        return ele

    @handle_selenium_exception
    def find_elements(self, locator_name: str, timeout: int = None, **kwargs) -> list:
        locator = self.modify_pom_locator(
            locators=self._locators, name=locator_name, value=kwargs.get('value'))

        """ 
            Find Multi Elements Methods
            These methods return a list elements belong to locator
        """
        WebDriverWait(self._driver, timeout if timeout else self.TIMEOUT).until(
            EC.presence_of_all_elements_located((locator['by'], locator['value'])))

        return self._driver.find_elements(locator['by'], locator['value'])

    @handle_selenium_exception
    def find_element_by_xpath_with_script(self, locator_name):
        """
        xpath attribute value must be use single quote (') character
        example: //div[@class='text']
        """
        xpath = self._locators[locator_name][1]
        script = 'var iterator = document.evaluate("%(xpath)s", document, null, XPathResult.ORDERED_NODE_ITERATOR_TYPE, null ); var thisNode = iterator.iterateNext(); return thisNode;'
        eles: WebElement = self.execute_script(script % {'xpath': xpath})
        return eles

    @handle_selenium_exception
    def find_elements_by_xpath_with_script(self, locator_name):
        """
        xpath attribute value must be use single quote (') character
        example: //div[@class='text']
        """
        xpath = self._locators[locator_name][1]
        script = "var iterator = document.evaluate(\"%(xpath)s\", document, null, XPathResult.UNORDERED_NODE_ITERATOR_TYPE, null );" \
                 "var arrayXpath = new Array();" \
                 "var thisNode = iterator.iterateNext();" \
                 "while (thisNode) {arrayXpath.push(thisNode);  thisNode = iterator.iterateNext(); }; return arrayXpath;"

        eles: WebElement = self.execute_script(script % {'xpath': xpath})
        return eles

    @handle_selenium_exception
    def find_elements_by_clss_nm_with_script(self, locator_name):
        class_name = self._locators[locator_name][1]
        eles: list[WebElement] = self.execute_script(
            f"return document.getElementsByClassName('{class_name}')")
        return eles

    def find_element_inside_element(self, element: WebDriver, locator_name: str, **kwargs):
        """
        xpath attribute value must be use single quote (') character
        example: //div[@class='text']
        """
        locator = self.modify_pom_locator(
            locators=self._locators, name=locator_name, value=kwargs.get('value'))
        retry_time = 1 if not kwargs.get(
            "retry_time") else kwargs.get("retry_time")
        for _ in range(retry_time):
            try:
                eles = element.find_element(locator['by'], locator['value'])
                return eles
            except (StaleElementReferenceException, NoSuchElementException, TimeoutException,
                    ElementClickInterceptedException) as e:
                logger.warn(Exception(
                    f'An exception of type occurred. With Element locator {locator["value"]}'))
            finally:
                if retry_time > 1:
                    TimeUtil.sleep(1)
                else:
                    pass

    @handle_selenium_exception
    def find_elements_inside_element(self, element: WebDriver, locator_name, **kwargs):
        locator = self.modify_pom_locator(
            locators=self._locators, name=locator_name, value=kwargs.get('value'))
        eles = element.find_elements(locator['by'], locator['value'])
        return eles

    """ 
        Checking Elements Methods
        These methods return a boolean expression (True or False).
    """

    def is_element_present(self, locator_name: str, timeout: int = None, **kwargs):
        return True if self.find_element(locator_name=locator_name, timeout=timeout,
                                         value=kwargs.get('value')) else False

    def is_element_gone(self, locator_name: str = None, timeout: int = None, **kwargs):
        loop_times = 0
        while loop_times < 2:
            try:
                element = kwargs.get('element')
                if element:
                    WebDriverWait(self._driver, timeout if timeout else self._wait_time_default).until(
                        EC.invisibility_of_element(element=element))
                else:
                    locator = self.modify_pom_locator(locators=self._locators, name=locator_name,
                                                      value=kwargs.get('value'))
                    WebDriverWait(self._driver, timeout if timeout else self._wait_time_default).until(
                        EC.invisibility_of_element((locator['by'], locator['value'])))
            except Exception as e:
                loop_times += 1
                logger.warn(f'Element: still visible, retrying!\n{e}')
            else:
                return True
        return False

    def is_element_displayed(self, locator_name: str, timeout: int = None, **kwargs) -> bool:
        return self.find_element(locator_name=locator_name, timeout=timeout, value=kwargs.get('value')).is_displayed()

    """ 
        Element Moving Action Methods
        These methods have action on element by Action Chains
    """

    def move_to_element_and_click(self, element):
        self.act_chains.move_to_element(element).click().perform()

    def scroll_to_view_element(self, element):
        self.execute_script(
            script=f"arguments[0].scrollIntoView();", arguments=element)

    def scroll_from_element(self, element_origin, x_offset=0, y_offset=0, delta_x=0, delta_y=0):
        """
        delta_x: distance scroll from the left
        delta_y: distance scroll from the bottom
        """
        origin = ScrollOrigin(origin=element_origin,
                              x_offset=x_offset, y_offset=y_offset)
        self.act_chains.scroll_from_origin(
            scroll_origin=origin, delta_x=delta_x, delta_y=delta_y).perform()

    """ 
        Element Click Action Methods
        These methods have action on element by selenium driver or script or other lib
    """

    def click_element_by_locator_with_script(self, locator_name: str, timeout: int = None, **kwargs):
        element = self.find_element(
            locator_name=locator_name, timeout=timeout, value=kwargs.get('value'))
        self.click_element_by_script(element)

    def click_element_by_script(self, element):
        self.move_to_element(element)
        self.execute_script("arguments[0].click()", element)

    def click_element(self, locator_name: str, timeout: int = None, **kwargs):
        self.find_element(locator_name=locator_name,
                          timeout=timeout, value=kwargs.get('value')).click()

    def click_random_element(self, locator_name: str, timeout: int = None, **kwargs):
        elements = self.find_elements(
            locator_name=locator_name, timeout=timeout, value=kwargs.get('value'))
        element: WebElement = random.choice(elements)
        text = element.text
        element.click()
        return text

    def double_click_by_action_chains(self, element):
        ActionChains(self._driver).double_click(element).perform()

    def click_by_action_chains(self, element):
        ActionChains(self._driver).click(element).perform()

    def press_key(self, key: str):
        self.act_chains.key_down(key).perform()

    """ 
        Element Send Action Methods
        These methods have action on element by selenium driver or script or other lib
    """

    def send_value(self, locator_name: str, text: str, timeout: int = None, **kwargs):
        ele = self.find_element(locator_name=locator_name,
                                timeout=timeout, value=kwargs.get('value'))
        ele.send_keys(text)

    def clear_and_send_value(self, locator_name: str, text: str, timeout: int = None, **kwargs):
        ele = self.find_element(locator_name=locator_name,
                                timeout=timeout, value=kwargs.get('value'))
        ele.clear()
        ele.send_keys(text)

    def delete_value_by_backspace(self, locator_name: str, timeout: int = None, **kwargs):
        """
            Action delete data by backspace to apply for mac
        """
        ele = self.find_element(locator_name=locator_name,
                                timeout=timeout, value=kwargs.get('value'))
        length = len(ele.get_attribute('value'))
        ele.send_keys(length * Keys.BACKSPACE)

    """ 
        Browser Action Methods
        These methods have action on element by selenium driver or script or other lib
    """

    def refresh_page(self):
        self._driver.refresh()

    def refresh_page_until_element_displayed(self, locator_name: str, value: str = None, timeout: int = None):
        self._driver.get(self.get_current_url())
        self.wait_until_element_displayed(
            locator_name=locator_name, timeout=timeout, value=value)

    def navigate_back(self):
        self._driver.back()

    def navigate_to_url(self, url):
        self._driver.get(url)

    def clear_browser_cookies(self):
        self._driver.delete_all_cookies()
        self.refresh_page()

    """ 
        Element Get and Set value Methods
        These methods set value to element attribute or return text / value of element
    """

    def set_attr_value(self, element, attr: str, value: str):
        self._driver.execute_script(
            f"arguments[0].setAttribute(\"{attr}\",\"{value}\")", element)

    def get_text_from_element(self, locator_name: str, timeout: int = None, **kwargs):
        ele = self.find_element(locator_name=locator_name,
                                timeout=timeout, value=kwargs.get('value'))
        return ele.text

    def get_attribute(self, locator_name: str, attr_mn: str, timeout: int = None, **kwargs):
        ele = self.find_element(locator_name=locator_name,
                                timeout=timeout, value=kwargs.get('value'))
        return ele.get_attribute(attr_mn)

    def get_css_value(self, locator_name: str, css_value: str, timeout: int = None, **kwargs):
        ele = self.find_element(locator_name=locator_name,
                                timeout=timeout, value=kwargs.get('value'))
        return ele.value_of_css_property(css_value)

    """ 
        Windows handles Methods
    """

    def get_window_handles(self):
        return self._driver.window_handles

    def get_window_size(self):
        return self._driver.get_window_size()

    def switch_window(self, window_id):
        child = self.get_window_handles()[window_id]
        self._driver.switch_to.window(child)

    """ 
        Page handles Methods
    """

    def wait_until_page_is_load_complete(self, timeout: int = None):
        WebDriverWait(self._driver,  timeout if timeout else self.TIMEOUT).until(
            lambda d: d.execute_script("return document.readyState") == "complete")

    def wait_until_element_displayed(self, locator_name: str, timeout: int = None, **kwargs):
        self.wait_until_page_is_load_complete()
        locator = self.modify_pom_locator(
            locators=self._locators, name=locator_name, value=kwargs.get('value'))
        WebDriverWait(self._driver, timeout if timeout else self.TIMEOUT).until(
            EC.presence_of_element_located((locator['by'], locator['value'])))

    def get_current_url(self):
        return self._driver.current_url

    def accept_browser_alert(self):
        self._driver.switch_to.alert.accept()

    def cancel_browser_alert(self):
        self._driver.switch_to.alert.dismiss()

    def get_text_browser_alert(self):
        return self._driver.switch_to.alert.text

    def switch_to_default_content(self):
        self._driver.switch_to.default_content()
