from typing import Dict
import os

# SELENIUM
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from cores.const.common import TimeConst
# LOCAL
from cores.const.web import BrowserConst
from cores.utils.common.logger_util import logger


class InitDriver:
    @staticmethod
    def create_driver(headless: bool = False, browser: str = 'chrome', page_load_strategy: str = "normal") -> WebDriver:
        try:
            if browser.lower() == BrowserConst.CHROME:
                options = webdriver.ChromeOptions()
                options.add_experimental_option(
                    'excludeSwitches', ['enable-logging'])

                # disable to skipped CORS error.
                options.add_argument("--disable-web-security")
                options.add_argument("--start-maximized")

                capa = DesiredCapabilities.CHROME
                capa["pageLoadStrategy"] = page_load_strategy  # "eager"

                # Accept microphone permissions POP UP
                options.add_experimental_option("prefs", {
                    "profile.default_content_setting_values.media_stream_mic": 1,
                })
            else:
                options = webdriver.FirefoxOptions()
                capa = DesiredCapabilities.FIREFOX
                capa["pageLoadStrategy"] = page_load_strategy  # "eager"

                # Accept microphone permissions POP UP
                options.set_preference(
                    "media.navigator.permission.disabled", True)
                options.set_preference(
                    "privacy.trackingprotection.enabled", False)

            if headless:
                options.add_argument("--no-sandbox")
                options.add_argument("--headless")
                options.add_argument("--window-size=2560,1600")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-gpu")
                options.add_argument("--allow-insecure-localhost")
                options.add_argument("--log-level=3")

                # Accept microphone permissions POP UP
                options.add_argument("--disable-infobars")
                options.add_argument("start-maximized")
                options.add_argument("--disable-extensions")
                # Enable fake UI for media stream
                options.add_argument("--use-fake-ui-for-media-stream")
                # Enable fake device for media stream
                options.add_argument("--use-fake-device-for-media-stream")
                cloud_options = {}
                options.set_capability('cloud:options', cloud_options)
            if browser.lower() == BrowserConst.CHROME:
                path = os.getenv('CHROME_PATH') if os.getenv(
                    'LOCAL_PATH') == 'NONE' else os.getenv('LOCAL_PATH')
                if not path:
                    driver = webdriver.Chrome(desired_capabilities=capa, service=Service(
                        ChromeDriverManager().install()), options=options)  # invalid since move to selenium 4.10
                else:
                    driver = webdriver.Chrome(service=Service(
                        executable_path=os.getenv('LOCAL_PATH')), options=options)
            else:
                driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager(cache_valid_range=1).install()),
                                           options=options)

            return driver
        except Exception as ex:
            logger.warning(f"Failed to create {browser} browser driver:\n{ex}")


class SeleniumDriver:
    TIMEOUT = TimeConst.Timeout.TIMEOUT_10

    def __init__(self, driver):
        self._driver: WebDriver = driver
        self.act_chains = ActionChains(driver)
        # self.touch_action = TouchAction(self._driver)

    def execute_script(self, script, arguments=None):
        if arguments:
            self._driver.execute_script(script, arguments)
        else:
            self._driver.execute_script(script)

    def switch_to_iframe(self, iframe):
        self._driver.switch_to.frame(iframe)

    def close_drive(self):
        self._driver.close()

    """ Methods """

    @staticmethod
    def modify_pom_locator(locators: dict, name: str, value=None) -> Dict:
        """
            - locator: locators dict
            - name: name of element in locator
            - value: use in case xpath need concat text
        """
        if value:
            return {'by': locators[name][2],
                    'value': locators[name][1] % value}
        else:
            return {'by': locators[name][2],
                    'value': locators[name][1]}
