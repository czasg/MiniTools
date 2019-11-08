import requests

from io import BytesIO
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from minitools.selenium.base import SeleniumBase

__all__ = 'ClickSelenium',


class ClickSelenium(SeleniumBase):

    def capture_interface(self):
        """You must enter the geetest capture interface in this func"""
        raise Exception("This func must be Implemented!")

    def get_click_img(self):
        element = self.waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".geetest_item_img")))
        self.sleep(2)
        return Image.open(BytesIO(requests.get(element.get_attribute('src')).content))

    def calculate_track(self, picture):
        """How to calculate the track?"""

    def click_each_gap(self, track):
        element = self.waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".geetest_item_img")))
        submit = self.waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.geetest_commit_tip')))
        for data in track:
            self.actors.move_to_element_with_offset(
                element, int(data['x']), int(data['y'])).click().perform()
            self.sleep(1)
        submit.click()

    def click_test(self):
        picture = self.get_click_img()  # get img@src pic
        track = self.calculate_track(picture)  # calculate the track so can click each gap to the order
        self.click_each_gap(track)  # click each gap by the track

    def check(self):
        """You Can add some check for result in here"""

    def run(self):
        self.capture_interface()
        self.click_test()
        self.check()
