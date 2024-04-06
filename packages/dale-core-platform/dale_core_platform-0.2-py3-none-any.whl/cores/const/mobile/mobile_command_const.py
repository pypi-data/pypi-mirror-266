class MobileCmdConst:
    class App:
        CLEAR_APP = 'mobile: clearApp'
        ACTIVATE_APP = 'mobile: activateApp'

    class Permission:
        SET_PERMISSION_ANDROID = 'mobile: changePermissions'
        GET_PERMISSION_ANDROID = 'mobile: getPermissions'
        SET_PERMISSION_IOS = 'mobile: setPermission'
        GET_PERMISSION_IOS = 'mobile: getPermission'
