from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains


class SeleniumBase:
    driver = None
    waiter = None
    _actors = None

    default_timeout = 20

    @property
    def actors(self):
        self._actors._actions[:] = []
        return self._actors

    def init_property(self):
        if self.driver:
            self.waiter = self.create_waiter()
            self._actors = ActionChains(self.driver)

    def create_waiter(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.default_timeout)

    def sleep(self, time_to_wait=0):
        self.driver.implicitly_wait(time_to_wait)
