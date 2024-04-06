import os
from typing import Dict

from cores.utils.common.store_util import GetUtil, StoreUtil
from cores.utils.common.time_util import TimeUtil
from cores.utils.common.path_util import PathUtil
from cores.utils.common.json_util import JsonConverterUtil
from cores.utils.common.logger_util import logger

from cores.const.common import TimeConst, EnvConst, PathConst
from cores.const.mobile import DeviceConst, CommandConst, CapabilitiesConst


class VirtualDevice:
    @staticmethod
    def start(platform: str):
        return VirtualDevice.start_android() if platform == EnvConst.Platform.ANDROID else VirtualDevice.start_ios()

    @staticmethod
    def start_android():
        os.environ[DeviceConst.Android.ANDROID_HOME] = os.getenv(DeviceConst.Android.ANDROID_HOME)
        os.popen(CommandConst.ADB.START_EMULATOR % {'device_name': os.getenv(CapabilitiesConst.DEVICE_NAME)})

        timer = 0
        time_out = 3
        while timer <= TimeConst.Timeout.TIMEOUT_60:
            TimeUtil.short_sleep(sleep_tm=time_out)
            active_devices = \
                os.popen(CommandConst.ADB.LIST_DEVICES).read().replace('\t',
                                                                       ' ').split("\n", 1)[1].split()
            if 'device' in active_devices:
                StoreUtil.suite_store(DeviceConst.Android.EMULATOR_NAME, active_devices[0])
                TimeUtil.short_sleep(sleep_tm=time_out)
                return True
            else:
                timer += time_out
        return False

    @staticmethod
    def start_ios():
        udid = GetUtil.suite_get(DeviceConst.iOS.UDID)

        # boot device
        os.popen(CommandConst.XCode.BOOT_DEVICE % {'uuid': udid})
        # start device
        start_vd = CommandConst.XCode.START_SIMULATOR % {'uuid': udid}
        os.popen(start_vd)
        timer = 0
        while timer <= TimeConst.Timeout.TIMEOUT_60:
            TimeUtil.short_sleep()
            active_devices = os.popen(
                CommandConst.XCode.GET_LIST_DEVICES).read()
            if udid in active_devices:
                return True
            else:
                timer += 5
        return False

    @staticmethod
    def stop(platform: str):
        if platform == EnvConst.Platform.ANDROID:
            command_kill_emulator = (CommandConst.ADB.KILL_EMULATOR %
                                     {'emulator_name': GetUtil.suite_get(DeviceConst.Android.EMULATOR_NAME)})
            os.popen(command_kill_emulator)
        else:
            os.popen(CommandConst.XCode.SHUTDOWN_DEVICE % {'uuid': GetUtil.suite_get(DeviceConst.iOS.UDID)})
            os.popen(CommandConst.XCode.KILL_SIMULATOR)
        logger.info(f"Stopped {platform} device!")

    @staticmethod
    def is_device_online():
        platform = os.getenv(CapabilitiesConst.PLATFORM_NAME)
        # if device offline => break flow
        if platform == EnvConst.Platform.ANDROID:
            is_online = CommandConst.ADB.DEVICE_OFFLINE_ERROR not in os.popen(CommandConst.ADB.LIST_DEVICES).read()
        elif platform == EnvConst.Platform.IOS:
            is_online = CommandConst.XCode.ERROR_NO_DEVICE_ONLINE not in os.popen(
                CommandConst.XCode.GET_LIST_DEVICES).read()
        else:
            raise Exception(f'Do not support {platform}!')
        if not is_online:
            raise (
                Exception(f'Device {CommandConst.ADB.DEVICE_OFFLINE_ERROR}'))
        return True

    @staticmethod
    def is_app_installed_on_device(platform: str):
        app_conf = GetUtil.suite_get(EnvConst.Environment.CONFIG_APP_OBJ)
        empty_cmd: str = ''
        if platform == EnvConst.Platform.ANDROID:
            is_app_installed = True if os.popen(CommandConst.ADB.GET_EXISTED_PACKAGE_APP % (
                GetUtil.suite_get(DeviceConst.Android.EMULATOR_NAME),
                app_conf.get(CapabilitiesConst.APP_PACKAGE))).read() != empty_cmd else False

        else:
            start_vd = CommandConst.XCode.GET_APP_BY_BUNDLE_ID % {'uuid': GetUtil.suite_get(DeviceConst.iOS.UDID),
                                                                  'bundle_id': app_conf.get(CapabilitiesConst.BUNDLE_IDENTIFIER)}
            is_app_installed = True if app_conf.get(DeviceConst.iOS.APP) in os.popen(start_vd).read() else False

        logger.debug(f"Is App installed on devices: {is_app_installed}")
        return is_app_installed

    @staticmethod
    def install_app(platform: str, is_cloud_app: bool = False):
        if VirtualDevice.is_device_online() and VirtualDevice.is_app_installed_on_device(platform):
            VirtualDevice.uninstall_app(platform)

        if platform == EnvConst.Platform.ANDROID:
            cmd = os.popen(CommandConst.ADB.INSTALL_APP % (GetUtil.suite_get(DeviceConst.Android.EMULATOR_NAME),
                                                           VirtualDevice.get_app_path(platform, is_cloud_app))).read()
        else:
            start_vd = CommandConst.XCode.INSTALL_APP % {'uuid': GetUtil.suite_get(DeviceConst.iOS.UDID),
                                                         'app_path': VirtualDevice.get_app_path(platform, is_cloud_app)}
            cmd = os.popen(start_vd).read()

        if CommandConst.ADB.FILE_NOT_FOUND_ERROR[0] == cmd or CommandConst.ADB.FILE_NOT_FOUND_ERROR[1] in cmd:
            raise (Exception(cmd))
        else:
            if VirtualDevice.waiting_to_process_app_complete(platform, is_install_method=True):
                logger.info(f"Installed  {platform} App!")
            else:
                logger.info(f"Install  {platform} App In-Complete!")

    @staticmethod
    def uninstall_app(platform: str):
        app_conf = GetUtil.suite_get(EnvConst.Environment.CONFIG_APP_OBJ)
        if platform == EnvConst.Platform.ANDROID:
            os.popen(CommandConst.ADB.REMOVE_APP % (GetUtil.suite_get(DeviceConst.Android.EMULATOR_NAME),
                                                    app_conf.get(CapabilitiesConst.APP_PACKAGE)))
        else:
            start_vd = CommandConst.XCode.UNINSTALL_APP % {'uuid': GetUtil.suite_get(DeviceConst.iOS.UDID),
                                                           'bundle_id': app_conf.get(CapabilitiesConst.BUNDLE_IDENTIFIER)}
            os.popen(start_vd)
        TimeUtil.short_sleep()
        if VirtualDevice.waiting_to_process_app_complete(platform, is_install_method=False):
            logger.info(f"Uninstalled  {platform} App!")
        else:
            logger.info(f"Uninstalled  {platform} App In-Complete!")

    @staticmethod
    def waiting_to_process_app_complete(platform: str, is_install_method: bool = True):
        TimeUtil.short_sleep()
        app_conf = GetUtil.suite_get(EnvConst.Environment.CONFIG_APP_OBJ)
        empty_cmd: str = ''

        def __is_completed(process_app_complete):
            if platform == EnvConst.Platform.ANDROID and is_install_method:
                return app_conf.get(CapabilitiesConst.APP_PACKAGE) in process_app_complete
            elif platform == EnvConst.Platform.IOS and is_install_method:
                return app_conf.get(DeviceConst.iOS.APP).lower() in process_app_complete.lower()
            else:
                return True if process_app_complete == empty_cmd else False

        timer = 0
        while timer <= TimeConst.Timeout.TIMEOUT_60:
            if platform == EnvConst.Platform.ANDROID:
                process_app_complete = os.popen(CommandConst.ADB.GET_EXISTED_PACKAGE_APP % (
                    GetUtil.suite_get(DeviceConst.Android.EMULATOR_NAME),
                    app_conf.get(CapabilitiesConst.APP_PACKAGE))).read()
            else:
                cmd = CommandConst.XCode.GET_APP_BY_BUNDLE_ID % {'uuid': GetUtil.suite_get(DeviceConst.iOS.UDID),
                                                                 'bundle_id': app_conf.get(CapabilitiesConst.BUNDLE_IDENTIFIER)}

                logger.info(f'Install app completed?')

                logger.debug(f'{cmd}')
                logger.info(f'Install app completed?\n {cmd}')
                process_app_complete = os.popen(cmd).read()

            if __is_completed(process_app_complete):
                return True
            else:
                timer += 5
        return False

    @staticmethod
    def get_app_path(platform: str, is_cloud_app: bool = False):
        app_conf = GetUtil.suite_get(
            EnvConst.Environment.CONFIG_APP_OBJ)
        if not os.getenv('INSTALL_PATH'):
            install_path = PathConst.INSTALL_ANDROID_APP_PATH if EnvConst.Platform.ANDROID else PathConst.INSTALL_IOS_APP_PATH
        else:
            install_path = os.getenv('INSTALL_PATH')
        if not is_cloud_app:
            app_path = DeviceConst.Android.APP if EnvConst.Platform.ANDROID == platform else DeviceConst.iOS.APP
            # if platform == EnvConst.Platform.ANDROID:
            #     path = f"{PathUtil.join_prj_root_path(install_path)}/{app_conf.get(DeviceConst.Android.APP)}"
            # else:
            #     path = f"{PathUtil.join_prj_root_path(install_path)}/{app_conf.get(DeviceConst.iOS.APP)}"
            path = f"{PathUtil.join_prj_root_path(install_path)}{app_conf.get(app_path)}"
            try:
                if PathUtil.is_path_correct(path):
                    return path
                else:
                    return f"{PathUtil.join_full_prj_root_path(install_path)}{app_conf.get(app_path)}"
            except Exception as e:
                raise Exception(f'Path {path} is not correct.\n{e}')
        else:
            # Waiting until app repo TODO
            pass

    @staticmethod
    def get_udid() -> Dict:
        """
        :return: Dictionary {os_version: [{name: device_model, udid: udid_str}]}
        e.g {'15.5': [{'name': 'iPhone 8', 'udid': '6BF8186C-9E62-48CF-AED4-05FD1D38FEF2'},
                        {'name': 'iPhone 8 Plus', 'udid': '46503C11-FF95-4DE1-81E4-8A2BC8B2DA4E'}],

        """
        r = os.popen(CommandConst.XCode.LIST_ALL_SIMULATORS)
        d = {}
        for k, v in JsonConverterUtil.convert_string_to_json(r.read())['devices'].items():
            if EnvConst.Platform.IOS.lower() in k.lower():
                name = k.split('.')[-1].replace('-', '.').replace('iOS.', '')
                tmp = []
                for i in v:
                    if 'iphone' or 'ipad' in i['name'].lower():
                        tmp.append({'name': i['name'], 'udid': i['udid']})
                d[name] = tmp
        return d

    @staticmethod
    def get_supported_udid(os_version: str, device_model: str) -> str:
        """
        :param os_version: iOS's os version. e.g. 15.5 or 16.0
        :param device_model:  iOS's device model. e.g. Iphone 14 Pro Max
        :return: udid string which is associated to the os and platform name
        """
        if os_version not in DeviceConst.iOS.SUPPORT_VERSION:
            raise Exception(
                f'Not support ios version: {os_version}. Support only: {DeviceConst.iOS.SUPPORT_VERSION}')
        else:
            try:
                for i in VirtualDevice.get_udid().get(os_version):
                    if i.get('name') == device_model:
                        return i.get('udid')
            except Exception as e:
                raise e

    @staticmethod
    def get_android_app_version(device_id: str, app_package: str):
        rs = os.popen(CommandConst.ADB.GET_APP_VERSION %
                      {'app_package': app_package,
                       'device_id': device_id})

        return rs.read().split('=')[1]

    @staticmethod
    def is_supported_android_version(version: str):
        return True if version in DeviceConst.Android.SUPPORT_VERSION else False

    @staticmethod
    def is_supported_ios_version(version: str):
        return True if version in DeviceConst.iOS.SUPPORT_VERSION else False

    @staticmethod
    def is_supported_platform(platform_name: str, platform_version: str):
        if platform_name.lower() == EnvConst.Platform.ANDROID.lower():
            return VirtualDevice.is_supported_android_version(platform_version)
        elif platform_name.lower() == EnvConst.Platform.IOS.lower():
            return VirtualDevice.is_supported_ios_version(platform_version)
        else:
            return False

