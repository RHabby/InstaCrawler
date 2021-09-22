from abc import ABC, abstractmethod
from typing import Dict, List

from fake_useragent import UserAgent
from fake_useragent.fake import FakeUserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class Auth(ABC):
    @abstractmethod
    def __init__(self, login: str, password: str) -> None:
        pass

    @abstractmethod
    def _configure_cookies(self, cookies: List) -> Dict:
        pass

    @abstractmethod
    def _process_auth(self) -> List:
        pass

    def get_cookies(self) -> Dict:
        credentials = self._process_auth()
        cookies = self._configure_cookies(credentials)

        return cookies

    def _configure_driver(self) -> WebDriver:
        options = self._configure_options()

        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(10)

        return driver

    def _configure_options(self) -> Options:
        user_agent = self._configure_user_agent()

        options = Options()
        options.page_load_strategy = "normal"
        options.add_argument("--headless")
        options.add_argument(f"user-agent={user_agent}")

        return options

    def _configure_user_agent(self) -> FakeUserAgent:
        ua = UserAgent()
        return ua.chrome


class InstaAuth(Auth):

    base_url: str = "https://www.instagram.com/"
    login: str
    password: str

    def __init__(self, login: str, password: str) -> None:
        self.login = login
        self.password = password

    def _configure_cookies(self, cookies: List) -> Dict:
        reqs = ("ig_did", "sessionid", "mid", "ds_user_id")
        return {
            cookie["name"]: cookie["value"]
            for cookie in cookies
            if cookie["name"] in reqs
        }

    def _process_auth(self) -> List:
        options = self._configure_options()

        with webdriver.Chrome(options=options) as driver:
            driver.get(self.base_url)
            wait = WebDriverWait(driver, 5)

            wait.until(ec.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#loginForm > div > div:nth-child(1) > div > label > input",
                ),
            )).send_keys(self.login)

            driver.find_element_by_css_selector(
                "#loginForm > div > div:nth-child(2) > div > label > input",
            ).send_keys(self.password)

            driver.find_element_by_css_selector(
                "#loginForm > div > div:nth-child(3) > button",
            ).click()

            try:
                wait.until(ec.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "#react-root > section > main > div > div > div > div > button",
                    ),
                )).click()
            finally:
                return driver.get_cookies()  # noqa
