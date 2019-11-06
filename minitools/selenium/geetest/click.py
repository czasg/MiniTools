import requests
import base64

from io import BytesIO
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from minitools.selenium.base import SeleniumBase


class ClickSelenium(SeleniumBase):

    def capture_interface(self):
        """You must enter the geetest capture interface in this func"""
        raise Exception("This func must be Implemented!")

    def get_click_img(self):
        self.waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".geetest_item_img")))
        element = self.driver.find_element_by_xpath('//*[@class="geetest_item_img"]')
        return Image.open(BytesIO(base64.b64encode(requests.get(element.get_attribute('src')).content)))

    def calculate_track(self, picture):
        pass

    def click_each_gap(self, track):
        pass

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
