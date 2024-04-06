import os
from typing import Any

from appium.webdriver.errorhandler import MobileErrorHandler
from appium.webdriver.webdriver import WebDriver

from cores.const.common import EnvConst
from cores.const.mobile import CapabilitiesConst
from cores.const.mobile.mobile_command_const import MobileCmdConst


class AppHelper:
    def __init__(self, driver):
        self.driver: WebDriver = driver
        self.platform = os.getenv(CapabilitiesConst.PLATFORM_NAME)

    def clear_app(self, app_id: str):
        """
        Deletes data files from the data container of an installed app,
        so it could start from the clean state next time it is launched.
        Args:
            app_id: The bundle identifier of the application to be cleared or
            The identifier of the application package to be cleared
        """
        if self.platform == EnvConst.Platform.ANDROID:
            data = {"appId": app_id}
        elif self.platform == EnvConst.Platform.IOS:
            data = {"bundleId": app_id}
        else:
            raise MobileErrorHandler(f'Do not support {self.platform} platform!')
        return self.driver.execute_script(MobileCmdConst.App.CLEAR_APP, data)

    def activate_app(self, app_id: str):
        """
        Activates the application if it is not running or is running in the background
        Args:
            app_id: the application id to be activated
        """
        if self.platform == EnvConst.Platform.ANDROID:
            data = {"appId": app_id}
        elif self.platform == EnvConst.Platform.IOS:
            data = {"bundleId": app_id}
        else:
            raise MobileErrorHandler(f'Do not support {self.platform} platform!')
        return self.driver.execute_script(MobileCmdConst.App.ACTIVATE_APP, data)

    def set_permission(self, permissions: str, app_id: str, **options: Any):
        """
        Changes package permissions in runtime.
        Args:
            permissions (string or list): One or more access rules to set.
                The following keys are supported: all (Apply the action to all services)
            app_id (required only iOS): The bundle identifier or app package of the destination app.
        Keyword Args:
            action (str): [Android only] Either grant (the default action) or revoke if target is set to pm,
                otherwise one of: allow (default), deny, ignore, default.
            target (str): [Android only]: Either pm (default) or appops (available since v2.11.0).
                The "appops" one requires adb_shell server security option to be enabled
        """
        if self.platform == EnvConst.Platform.ANDROID:
            data = {"permissions": permissions, "appId": app_id}
            if options:
                data.update({'options': options})
            return self.driver.execute_script(MobileCmdConst.Permission.SET_PERMISSION_ANDROID, data)
        elif self.platform == EnvConst.Platform.IOS:
            data = {"access": permissions, "bundleId": app_id}
            return self.driver.execute_script(MobileCmdConst.Permission.SET_PERMISSION_IOS, data)
        else:
            raise MobileErrorHandler(f'Do not support {self.platform} platform!')