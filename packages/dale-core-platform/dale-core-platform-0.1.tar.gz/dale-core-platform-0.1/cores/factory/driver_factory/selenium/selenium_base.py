from .selenium_actions import SeleniumActions


class SeleniumBase(SeleniumActions):

    def __init__(self, driver):
        super().__init__(driver)
