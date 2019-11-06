import random

from io import BytesIO
from PIL import Image, ImageChops
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from minitools.selenium.base import SeleniumBase

__all__ = "SlideSelenium",


class SlideSelenium(SeleniumBase):

    def capture_interface(self):
        raise NotImplementedError("You must enter the geetest capture interface in this func")

    def get_slide_img(self, full=True):
        slide_img = self.waiter.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_slice")))
        full_img = self.waiter.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "canvas.geetest_canvas_fullbg")))
        self.sleep(2)
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
        pic_diff = ImageChops.difference(image1, image2)
        pic_diff = pic_diff.convert("L")
        table = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        pic_diff = pic_diff.point(table, '1')
        left = 43
        pic_diff_rec = pic_diff.load()
        for w in range(pic_diff.size[0] - 1, left, -1):
            count = 0
            for h in range(pic_diff.size[1] - 1, 0, -1):
                if pic_diff_rec[w, h] == 1:
                    count += 1
                    if count > 5:
                        return w - left

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
        track = self.calculate_track(gap)  # calculate the track so can move button to the gap
        self.move_to_gap(track)  # move the button to the gap by track

    def check(self):
        """You Can add some check for result in here"""

    def run(self):
        self.capture_interface()
        self.slide_test()
        self.check()
