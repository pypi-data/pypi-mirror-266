# pylint:disable=too-few-public-methods
""" Combine Locust with Selenium Web Driver """

from locust import User
from locust.exception import LocustError
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from .core import RealBrowserClient
from cores.utils.common.logger_util import logger


class RealBrowserLocust(User):
    """
   This is the abstract Locust class which should be subclassed.
   """
    client = None
    timeout = 30
    screen_width = 2560
    screen_height = 1600

    def __init__(self, environment):
        super(RealBrowserLocust, self).__init__(environment=environment)
        if self.screen_width is None:
            raise LocustError("You must specify a screen_width "
                              "for the browser")
        if self.screen_height is None:
            raise LocustError("You must specify a screen_height "
                              "for the browser")


class ChromeLocust(RealBrowserLocust):
    """
    Provides a Chrome webdriver that logs GET's and waits to locust
    """

    def __init__(self, environment):
        super(ChromeLocust, self).__init__(environment=environment)
        self.client = RealBrowserClient(
            webdriver.Chrome(),
            self.timeout,
            self.screen_width,
            self.screen_height
        )


class HeadlessChromeLocust(RealBrowserLocust):
    """
    Provides a headless Chrome webdriver that logs GET's and waits to locust
    """

    def __init__(self, environment):
        super(HeadlessChromeLocust, self).__init__(environment)
        options = webdriver.ChromeOptions()
        options.add_argument('headless')
        options.add_argument('window-size={}x{}'.format(
            self.screen_width, self.screen_height
        ))
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--log-level=3")
        capa = DesiredCapabilities.CHROME
        capa["pageLoadStrategy"] = "eager"

        driver = webdriver.Chrome(desired_capabilities=capa, service=Service(
            ChromeDriverManager().install()), options=options)

        logger.info('Actually trying to run headless Chrome')
        self.client = RealBrowserClient(
            driver,
            self.timeout,
            self.screen_width,
            self.screen_height,
            set_window=False
        )


class FirefoxLocust(RealBrowserLocust):
    """
    Provides a Firefox webdriver that logs GET's and waits to locust
    """

    def __init__(self, environment):
        super(FirefoxLocust, self).__init__(environment)
        self.client = RealBrowserClient(
            webdriver.Firefox(),
            self.timeout,
            self.screen_width,
            self.screen_height
        )
