import os
from typing import Any, Dict

from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.options.ios import XCUITestOptions
from appium.webdriver.webdriver import WebDriver

from cores.const.common import EnvConst, TimeConst
from cores.const.custom_exception import DriverAppError
from cores.const.mobile import AppiumServerConst, CapabilitiesConst
from cores.utils.common.logger_util import logger
from cores.utils.common.store_util import GetUtil
from ..appium.virtual_device import VirtualDevice


class MobileDriver:
    TIMEOUT = TimeConst.Timeout.TIMEOUT_10

    def __init__(self, driver):
        self.driver: WebDriver = driver

    @staticmethod
    def modify_locator(locators: dict, name: str, value=None) -> Dict:
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

    @staticmethod
    def create_android_driver(custom_opts: Dict[str, Any]):
        options = UiAutomator2Options()
        options.load_capabilities(custom_opts)
        return webdriver.Remote(GetUtil.suite_get(AppiumServerConst.OBJ).get(AppiumServerConst.REMOTE_PATH),
                                options=options)

    @staticmethod
    def create_ios_driver(custom_opts: Dict[str, Any]):
        options = XCUITestOptions()
        options.load_capabilities(custom_opts)
        return webdriver.Remote(GetUtil.suite_get(AppiumServerConst.OBJ).get(AppiumServerConst.REMOTE_PATH),
                                options=options)

    @staticmethod
    def gen_capabilities():
        app_conf = GetUtil.suite_get(EnvConst.Environment.CONFIG_APP_OBJ)
        platform_name = os.getenv(CapabilitiesConst.PLATFORM_NAME)
        platform_version = os.getenv(CapabilitiesConst.PLATFORM_VERSION)
        device_name = os.getenv(CapabilitiesConst.DEVICE_NAME)

        if platform_name.lower() == EnvConst.Platform.ANDROID.lower():
            caps = dict(platformVersion=platform_version,
                        deviceName=device_name,
                        autoGrantPermissions=True,
                        appPackage=app_conf.get(CapabilitiesConst.APP_PACKAGE),
                        appActivity=app_conf.get(CapabilitiesConst.APP_ACTIVITIES))
        else:
            caps = dict(platformVersion=platform_version,
                        deviceName=device_name,
                        bundleId=app_conf.get(CapabilitiesConst.BUNDLE_IDENTIFIER))
        return caps

    @staticmethod
    def mobile_driver_factory(platform_name: str, platform_version: str, custom_opts: Dict[str, Any]):
        if VirtualDevice.is_supported_platform(platform_name=platform_name, platform_version=platform_version):
            try:
                if platform_name.lower() == EnvConst.Platform.ANDROID.lower():
                    driver = MobileDriver.create_android_driver(custom_opts)
                else:
                    driver = MobileDriver.create_ios_driver(custom_opts)
                logger.info(f"Started {platform_name} driver!")
                return driver
            except Exception:
                raise DriverAppError(f'Cannot started {platform_name} driver')
        else:
            logger.error(f"Not support platform: {platform_name} on version {platform_version}")
