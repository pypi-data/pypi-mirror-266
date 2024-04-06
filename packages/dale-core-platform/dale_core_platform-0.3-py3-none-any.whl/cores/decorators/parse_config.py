import configparser
import os
from functools import wraps

from ..const.common import EnvConst as const
from ..const.mobile import AppiumServerConst, DeviceConst, CapabilitiesConst
from ..factory.driver_factory.appium.virtual_device import VirtualDevice
from ..model.db_conn import DbConnModel
from ..utils.common.path_util import PathUtil
from ..utils.common.store_util import StoreUtil
from ..utils.common.string_util import StringUtil


def parse_db_config(db_type: str):
    """_summary_

    Args:
        db_type (str): _description_
    """
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            config = configparser.RawConfigParser()
            config.read(PathUtil.join_prj_root_path(
                const.ConfigPath.DB_CONFIG))
            _p = {'db_name': config[db_type].get(const.Database.DB_NAME),
                  'db_host': config[db_type].get(const.Database.DB_HOST),
                  'db_port': str(config[db_type].get(const.Database.DB_PORT)),
                  'db_username': os.getenv(const.Database.DB_USERNAME),
                  'db_pwd': os.getenv(const.Database.DB_PWD)
                  }
            db_obj: DbConnModel = DbConnModel(**_p)
            StoreUtil.suite_store(const.Database.DB_OBJ, db_obj)
            function(*args, **kwargs)
        return wrapper
    return decorator


def parse_driver_config(platform_name: str):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            appium_config_path = PathUtil.get_prj_root_path() + const.ConfigPath.APPIUM_CONFIG_PATH
            appium_config = configparser.RawConfigParser()
            appium_config.read(appium_config_path)
            if const.Platform.IOS in platform_name:
                StoreUtil.suite_store(DeviceConst.iOS.UDID,
                                      VirtualDevice.get_supported_udid(os_version=os.getenv(key=CapabilitiesConst.PLATFORM_VERSION),
                                                                       device_model=os.getenv(key=CapabilitiesConst.DEVICE_NAME)))

            StoreUtil.suite_store(AppiumServerConst.OBJ, appium_config[AppiumServerConst.OBJ])
            function(*args, **kwargs)
        return wrapper
    return decorator


def parse_app_config(app_name: str):
    def decorator(function):
        @wraps(function)
        def wrapper(*args, **kwargs):
            file = PathUtil.get_prj_root_path() + const.ConfigPath.APP_CONFIG_PATH % {'name': app_name}
            config = configparser.RawConfigParser()
            config.read(file)
            StoreUtil.suite_store(const.Environment.CONFIG_APP_OBJ, config[app_name])
            function(*args, **kwargs)

        return wrapper

    return decorator
