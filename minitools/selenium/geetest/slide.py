import random

from io import BytesIO
from PIL import Image
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from minitools.selenium.base import SeleniumBase

__all__ = "SlideSelenium",


class SlideSelenium(SeleniumBase):
    THRESHOLD = 60
    LEFT = 60
    BORDER = 0

    def capture_interface(self):
        """You must enter the geetest capture interface in this func"""
        raise Exception("This func must be Implemented!")

    def get_slide_img(self, full=True):
        slide_img = self.waiter.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_slice")))
        full_img = self.waiter.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_fullbg")))
        if full:
            self.driver.execute_script(
                'document.getElementsByClassName("geetest_canvas_fullbg")[0].setAttribute("style", "")')
        else:
            self.driver.execute_script(
                "arguments[0].setAttribute(arguments[1], arguments[2])", full_img, "style", "display: none")
        location = slide_img.location
        size = slide_img.size
        top, bottom, left, right = location["y"], location["y"] + \
                                   size["height"], location["x"], location["x"] + size["width"]
        screenshot = self.get_screenshot()
        captcha = screenshot.crop(
            (left, top, right, bottom))
        size = size["width"] - 1, size["height"] - 1
        captcha.thumbnail(size)
        return captcha

    def get_screenshot(self):
        screenshot = self.driver.get_screenshot_as_png()
        return Image.open(BytesIO(screenshot))

    def calculate_gap(self, image1, image2):
        for i in range(self.LEFT, image1.size[0]):
            for j in range(image1.size[1]):
                if not self.is_pixel_equal(image1, image2, i, j):
                    return i
        return self.LEFT

    def is_pixel_equal(self, image1, image2, x, y):
        pixel1 = image1.load()[x, y]
        pixel2 = image2.load()[x, y]
        if abs(pixel1[0] - pixel2[0]) < self.THRESHOLD and \
                abs(pixel1[1] - pixel2[1]) < self.THRESHOLD and \
                abs(pixel1[2] - pixel2[2]) < self.THRESHOLD:
            return True
        else:
            return False

    def calculate_track(self, distance):
        track = []
        current = 0
        mid = distance * 2 / 3
        t = 0.2
        v = 0
        distance += 10
        while current < distance:
            if current < mid:
                a = random.randint(1, 3)
            else:
                a = -random.randint(3, 5)
            v0 = v
            v = v0 + a * t
            move = v0 * t + 0.5 * a * t * t
            current += move
            track.append(round(move))
        for i in range(2):
            track.append(-random.randint(2, 3))
        for i in range(2):
            track.append(-random.randint(1, 4))
        return track

    def move_to_gap(self, track):
        button = self.waiter.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="geetest_slider_button"]')))
        self.actors.click_and_hold(button).perform()
        for i in track:
            self.actors.move_by_offset(xoffset=i, yoffset=0).perform()
            self.sleep(0.0005)
        self.sleep(0.5)
        self.actors.release().perform()

    def slide_test(self):
        picture1 = self.get_slide_img(True)  # get first full picture
        picture2 = self.get_slide_img(False)  # get second incomplete picture
        gap = self.calculate_gap(picture1, picture2)  # calculate the gap between pictures
        track = self.calculate_track(gap - self.BORDER)  # calculate the track so can move button to the gap
        self.move_to_gap(track)  # move the button to the gap by track

    def check(self):
        """You Can add some check for result in here"""

    def run(self):
        self.capture_interface()
        self.slide_test()
        self.check()
