import os
from ..__const import Const


class CommandConst(Const):
    class ADB:
        __android_home = os.getenv("ANDROID_HOME")
        ADB_PATH = __android_home + "/platform-tools/adb"
        EMULATOR_PATH = __android_home + "/emulator/emulator"
        # device_name
        START_EMULATOR = EMULATOR_PATH + ' -avd %(device_name)s -no-snapshot-load -netdelay none -netspeed full > logs/adb_log.txt'
        LIST_DEVICES = ADB_PATH + ' devices'
        KILL_EMULATOR = ADB_PATH + ' -s %(emulator_name)s emu kill'  # emulator_name
        # get app package from list
        GET_EXISTED_PACKAGE_APP = ADB_PATH + ' -s %s shell pm list packages | grep %s'
        INSTALL_APP = ADB_PATH + ' -s %s install %s'  # install app to android from data
        REMOVE_APP = ADB_PATH + ' -s %s uninstall %s'  # uninstall app from android device
        FILE_NOT_FOUND_ERROR = ['Performing Streamed Install',
                                "The operation couldn't be completed. No such file or directory"]
        DEVICE_OFFLINE_ERROR = 'offline'
        GET_APP_VERSION = 'adb -s %(device_id)s shell dumpsys package %(app_package)s | grep versionName'

    class XCode:
        # udid
        START_SIMULATOR = 'open -a Simulator --args -CurrentDeviceUDID %(uuid)s'
        KILL_SIMULATOR = 'killall Simulator'
        GET_LIST_DEVICES = 'xcrun simctl getenv booted SIMULATOR_UDID'
        INSTALL_APP = 'xcrun simctl install %(uuid)s %(app_path)s'
        UNINSTALL_APP = 'xcrun simctl uninstall %(uuid)s %(bundle_id)s'
        GET_APP_BY_BUNDLE_ID = 'xcrun simctl get_app_container %(uuid)s %(bundle_id)s'
        LIST_ALL_SIMULATORS = 'xcrun simctl list devices --json'
        ERROR_NO_DEVICE_ONLINE = 'No devices are booted'
        SHUTDOWN_DEVICE = 'xcrun simctl shutdown %(uuid)s'
        BOOT_DEVICE = 'xcrun simctl boot %(uuid)s'
