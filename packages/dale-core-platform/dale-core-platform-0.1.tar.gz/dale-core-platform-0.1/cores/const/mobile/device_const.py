from ..__const import Const


class DeviceConst(Const):
    IS_CLOUD_APP = "IS_CLOUD_APP"
    APP_REQUIRED = "APP_REQUIRED"

    class Android:
        SUPPORT_VERSION = ['14.0', '12.0', '13.0']
        ANDROID_HOME = "ANDROID_HOME"
        APP = "ANDROID_APP"
        EMULATOR_NAME = "EMULATOR_NAME"

    class iOS:
        SUPPORT_VERSION = ['16.0', '16.2', '16.3', '16.4']
        APP = "APP"
        UDID = "UDID"
        
