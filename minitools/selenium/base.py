import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains


class SeleniumBase:
    driver = None
    waiter = None
    _actors = None

    default_timeout = 20
    clear_level = 0

    def __del__(self):
        if self.clear_level == 0:
            pass
        elif self.clear_level == 1:
            self.driver.close()
        elif self.clear_level == 2:
            self.driver.quit()

    @property
    def actors(self):
        self._actors._actions[:] = []
        return self._actors

    def init_property(self):
        if self.driver:
            self.waiter = self.create_waiter()
            self._actors = ActionChains(self.driver)
        self.driver.implicitly_wait(self.default_timeout)

    def create_waiter(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.default_timeout)

    def sleep(self, time_to_wait=0):
        time.sleep(time_to_wait)
