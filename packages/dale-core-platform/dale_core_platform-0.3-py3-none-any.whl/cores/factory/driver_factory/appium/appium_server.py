from appium.webdriver.appium_service import AppiumService
from cores.const.mobile import AppiumServerConst
from cores.const.common import TimeConst
from cores.utils.common.logger_util import logger
from cores.utils.common.store_util import GetUtil, StoreUtil


class AppiumServer:
    @staticmethod
    def start(timeout: int = TimeConst.Timeout.TIMEOUT_60000MS):
        appium_config = GetUtil.suite_get(AppiumServerConst.OBJ)
        service = AppiumService()
        if service.is_running:
            service.stop()
        if service.start(args=['--address', appium_config.get(AppiumServerConst.HOST),
                               '-p', appium_config.get(AppiumServerConst.PORT)],
                         timeout_ms=timeout):
            StoreUtil.suite_store(AppiumServerConst.SERVICE, service)
            logger.info("Started Appium Server!")
            return True
        else:
            logger.info("Can't start Appium Server!")
            return False

    @staticmethod
    def stop():
        GetUtil.suite_get(AppiumServerConst.SERVICE).stop()
        logger.info("Stopped Appium Server!")
