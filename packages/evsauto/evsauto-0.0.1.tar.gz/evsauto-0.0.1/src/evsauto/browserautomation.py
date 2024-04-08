from time import sleep
from glob import glob
import os

from evsauto.utils import get_file_count
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from webdriver_manager.firefox import GeckoDriverManager


class WebDriverWrapper:
    """
    A class that wraps a selenium webdriver in order to
    improve code readability and encourage rapid prototyping.
    """

    def __init__(self, **kwargs):
        # setup variables for context manager
        self.driver = None
        self.actions = None
        self.wait = None

        # setup variables for instance
        self.download_path = kwargs.pop("download_path", None)
        self.headless = kwargs.pop("headless", False)
        self.log_path = kwargs.pop("log_path", "webdriver_log.txt")
        self.default_timeout = kwargs.pop("default_timeout", 30)
        self.max_timeout = kwargs.pop("max_timeout", 300)

        # get the default profile
        self._base_profile_path = os.path.join(
            os.getenv("APPDATA"), "Mozilla", "Firefox", "Profiles"
        )
        self._profile_list = glob(
            os.path.join(self._base_profile_path, "*.default-esr")
        )

        # setup webdriver options and preferences
        self.options = webdriver.FirefoxOptions()

        self.options.add_argument("-width=1920")
        self.options.add_argument("-height=1080")
        self.options.add_argument(f"-profile={self._profile_list[0]}")
        if self.headless:
            self.options.add_argument("--headless")

        if self.download_path:
            self.options.set_preference("browser.download.folderList", 2)
            self.options.set_preference("browser.download.dir", self.download_path)

    def __enter__(self):
        # configure and assign a webdriver to self
        service = webdriver.FirefoxService(
            executable_path=GeckoDriverManager().install()
        )

        self.driver = webdriver.Firefox(service=service, options=self.options)
        self.driver.implicitly_wait(0)

        self.actions = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, self.default_timeout, 0.1)

        return self

    def __exit__(self, exc_type, exc_value, exc_trace):
        # close the webdriver
        self.driver.quit()
        del self.driver
        del self.actions
        del self.wait

    def get(self, url):
        """
        Navigate to the given URL on the window/frame in focus.
        """
        self.driver.get(url)

    def new_tab(self, url):
        """
        Open the given URL in a new tab and apply focus.
        """
        self.driver.execute_script(f"window.open('{url}');")
        self.driver.switch_to.window(
            self.driver.window_handles[len(self.driver.window_handles) - 1]
        )

    def goto_tab(self, tab_index):
        """
        Open the tab corresponding to the given tab_index.
        """
        self.driver.switch_to.window(self.driver.window_handles[tab_index])

    def close_all_tabs(self) -> None:
        """
        Close all tabs except for the first one opened.
        """
        for i in range(len(self.driver.window_handles) - 1, -1, -1):
            if i == 0:
                self.driver.switch_to.window(self.driver.window_handles[i])
                break
            self.driver.switch_to.window(self.driver.window_handles[i])
            self.driver.close()

    # def find_element(self, selector, type="presence"):
    #     element = None
    #     if type == "presence":
    #         element = self.wait.until(
    #             EC.presence_of_element_located((By.XPATH, selector))
    #         )
    #     elif type == "clickable":
    #         element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
    #     return element

    def find_element(self, selector, type="presence"):
        element = None
        if type == "presence":
            element = self.wait.until(
                EC.visibility_of_element_located((By.XPATH, selector))
            )
        elif type == "clickable":
            element = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
        return element

    def find_elements(self, selector, type="presence"):
        elements = None
        if type == "presence":
            __ = self.wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            elements = self.driver.find_elements("xpath", selector)
        elif type == "clickable":
            __ = self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            elements = self.driver.find_elements("xpath", selector)
        return elements

    def wait_until_enabled(self, selector):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, selector)))

    def wait_until_gone(self, selector):
        self.wait.until(EC.invisibility_of_element((By.XPATH, selector)))

    def click_element(self, element, javascript_click=False):
        if javascript_click:
            self.driver.execute_script("arguments[0].click();", element)
        else:
            self.actions.click(element).perform()

    def type_into_element(
        self, element, content, use_javascript=False, send_enter=False
    ):
        if use_javascript:
            self.driver.execute_script(
                f"arguments[0].setAttribute('value', '{content}');", element
            )
        else:
            self.actions.click(element).send_keys(content).perform()
            if send_enter:
                self.actions.click(element).send_keys(Keys.RETURN).perform()

    def wait_until_downloaded(self, count) -> bool:
        """
        Waits until 'count' downloaded files
        exist before the timeout is reached. Returns
        False if the timeout is exceeded. Returns True if
        'count' files exist.
        """
        if not self.download_path:
            raise AttributeError(
                "A download path must be specified in order to call wait_until_downloaded."
            )

        download_timeout = 0
        while (
            download_timeout < self.max_timeout
            and get_file_count(self.download_path) < count
        ):
            download_timeout += 1
            sleep(1)
        if download_timeout >= self.max_timeout:
            return False
        return True
