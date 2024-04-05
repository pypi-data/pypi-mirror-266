"""
Copyright (c) 2023 Plugin Andrey (9keepa@gmail.com)
Licensed under the MIT License
"""
from abc import ABCMeta, abstractmethod
from typing import Dict, Union, List, TypedDict
from selenium.webdriver.remote.webdriver import WebDriver
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from web_render.tool import log
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
import platform
import subprocess


logger = log(__name__)

current_platform = platform.system()

if current_platform == "Windows":
    def get_google_chrome_version():
        try:
            cmd = 'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True, shell=True)
            version = result.strip()
            return version
        except subprocess.CalledProcessError as e:
            logger.info(f"Error executing google-chrome-stable: {e}")
            return None

elif current_platform == "Linux":
    logger.info("Running on Linux")
    def get_google_chrome_version():
        try:
            cmd = ["google-chrome-stable", "--version"]
            result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
            version = result.strip()
            return version
        except subprocess.CalledProcessError as e:
            logger.info(f"Error executing google-chrome-stable: {e}")
            return None
elif current_platform == "Darwin":
    raise RuntimeError(f"Platform {current_platform} not support")
else:
    raise RuntimeError(f"Platform {current_platform} not support")


def get_chromedriver_version(chromedriver_path):
    try:
        cmd = [chromedriver_path, "--version"]
        result = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        version = result.strip().split()[1]
        return version
    except subprocess.CalledProcessError as e:
        logger.info(f"Error executing Chromedriver: {e}")
        return None


# Определяем тип TypedDict с определенными ключами и типами значений
class IWebWait(TypedDict):
    name: str
    params: Dict


class AbstractRender(metaclass=ABCMeta):

    @abstractmethod
    def __init__(self, browser):
        self.browser = browser

    @abstractmethod
    def set_url(self, *args, **kwargs):
        pass

    @abstractmethod
    def get_content(self, *args, **kwargs):
        pass

    @abstractmethod
    def quit(self, *args, **kwargs):
        pass


class SeleniumRender(AbstractRender):

    def __init__(self, browser: WebDriver):
        self.browser = browser
        self._web_driver_wait = WebDriverWait(self.browser, 10)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()

    def _web_wait(self, items: Union[IWebWait, List[IWebWait]]):
        if isinstance(items, list):
            for item in items:
                target: Union[
                    CheckElementInDOM,
                    CheckNumberElementsInPage
                ] = web_wait_class[item['name']]
                self._web_driver_wait.until(target(**item['params']))

        if isinstance(items, dict):
            target: Union[
                CheckElementInDOM,
                CheckNumberElementsInPage
            ] = web_wait_class[items['name']]
            self._web_driver_wait.until(target(**items['params']))

    def set_url(self, url, web_wait: Union[IWebWait, List[IWebWait], None]=None):
        self.browser.get(url)

        if web_wait:
            self._web_wait(web_wait)

    def get_content(self):
        return self.browser.page_source

    def quit(self):
        self.browser.quit()
        logger.info(f"Close {self.browser}")


def make_selenium_webdriver(config: Dict):
    co = Options()
    if config.get("PROXY_SERVER"):
        co.add_argument(
            "--proxy-server={}".format(config['PROXY_SERVER']))
    if config.get('HEADLESS'):
        co.add_argument('--headless=new')

    co.add_argument('--disable-blink-features=AutomationControlled')
    co.add_argument('--no-sandbox')
    co.add_argument('--disable-dev-shm-usage')
    co.add_argument("start-maximized")
    if config.get('INCOGNITO'):
        co.add_argument("--incognito")
    co.add_experimental_option("excludeSwitches", ["ignore-certificate-errors"])
    co.add_experimental_option("excludeSwitches", ["enable-automation"])
    co.add_experimental_option('useAutomationExtension', False)

    if config.get('DISABLE_IMAGE'):
        chrome_prefs = {}
        chrome_prefs["profile.default_content_settings"] = {"images": 2}
        chrome_prefs["profile.managed_default_content_settings"] = {"images": 2}
        co.add_experimental_option("prefs", chrome_prefs)


    download_driver = Service(ChromeDriverManager(
        driver_version=config.get('CHROME_DRIVER_VERSION')
    ).install())

    # -- Version
    google_chrome_version = get_google_chrome_version()
    if google_chrome_version:
        logger.info(f"Google Chrome version: {google_chrome_version}")

    chromedriver_version = get_chromedriver_version(download_driver.path)
    if chromedriver_version:
        logger.info(f"Chromedriver version: {chromedriver_version}")
    ### --

    if config.get('UNDETECTED_CHROMEDRIVER'):
        driver = uc.Chrome(headless=config.get('HEADLESS'))
    else:
        driver = webdriver.Chrome(service=download_driver, options=co)

    if config.get('LOAD_TIMEOUT'):
        driver.set_page_load_timeout(config['LOAD_TIMEOUT'])
    return driver


class CheckElementInDOM:

    def __init__(self, css_selectors: List[str]):
        self.css_selectors = css_selectors

    def check_elements(self, driver: WebDriver):
        for css_selector in self.css_selectors:
            try:
                driver.find_element(By.CSS_SELECTOR, css_selector)
            except NoSuchElementException:
                return False
        return True

    def __call__(self, driver: WebDriver):
        return self.check_elements(driver)


class CheckNumberElementsInPage:

    def __init__(self, selector, count):
        self.css_selector: str = selector
        self.quantity: int = count

    def check_elements(self, driver: WebDriver):
        elements = driver.find_elements(By.CSS_SELECTOR, self.css_selector)
        if len(elements) >= self.quantity:
            return True
        return False

    def __call__(self, driver: WebDriver):
        return self.check_elements(driver)


web_wait_class = {
    "CheckElementInDOM" : CheckElementInDOM,
    "CheckNumberElementsInPage": CheckNumberElementsInPage
}
