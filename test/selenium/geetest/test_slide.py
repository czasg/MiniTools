from selenium import webdriver

from selenium.webdriver.common.by import By
from minitools.selenium.geetest import SlideSelenium
from selenium.webdriver.support import expected_conditions as EC

"""
BiLiBiLi: 模拟登陆
https://passport.bilibili.com/login
"""

class BiliBiliLogin(SlideSelenium):
    def __init__(self, account, password):
        self.account = account
        self.password = password
        self.driver = webdriver.Chrome('D:\chromedriver.exe')
        self.driver.get("https://passport.bilibili.com/login")
        self.init_property()

    def run(self):
        username = self.waiter.until(EC.element_to_be_clickable((By.ID, 'login-username')))
        passwd = self.waiter.until(EC.element_to_be_clickable((By.ID, 'login-passwd')))
        button = self.waiter.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="btn btn-login"]')))
        username.clear()
        passwd.clear()
        self.sleep(0.1)
        username.send_keys(self.account)
        passwd.send_keys(self.password)
        self.sleep(2)
        button.click()


if __name__ == '__main__':
    account = 'test'
    password = 'test'
    test = BiliBiliLogin(account, password)
    test.run()
    test.slide_test()


