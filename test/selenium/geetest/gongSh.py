import requests
import base64
import logging

from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from minitools.selenium.geetest import ClickSelenium
from minitools import init_logging_format

init_logging_format()

CLICK_API = ""
PROXY_API = ""
gongS_API = "http://www.gsxt.gov.cn/index.html"
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def api_get_click_position(body):
    body = base64.b64encode(body).decode()
    return requests.post(CLICK_API, json={
        'model_site': 'jiyanyuxu',
        'image': body
    }).json()


def get_wan_proxy(proxy_url=None, p=None):
    if proxy_url is None:
        proxy_url = PROXY_API
    params = {"pay": str(p)} if p else {}
    res = requests.get(proxy_url, params=params)
    logger.info("获取到代理:" + str(res.text))
    assert res.status_code == 200, "获取代理结果异常:" + res.text
    return res.text


class ChuangYuAntiSpider(Exception):
    """创宇验证码反爬"""


class IdentifyMistakes(Exception):
    """验证码识别错误"""


class GongSh(ClickSelenium):

    def __init__(self, search, debug=False, use_proxy=False):
        self.search = search
        self.max_run = 2
        options = webdriver.ChromeOptions()
        None if debug else options.add_argument('--headless')
        None if not use_proxy else options.add_argument("--proxy-server=http://{}".format(get_wan_proxy(p=1)))
        self.driver = webdriver.Chrome('D:\chromedriver.exe', options=options)
        self.init_property()

    def capture_interface(self):
        self.driver.get(gongS_API)
        try:
            search = self.waiter.until(EC.element_to_be_clickable((By.ID, 'keyword')))
            submit = self.waiter.until(EC.element_to_be_clickable((By.ID, 'btn_query')))
        except (TimeoutException, NoSuchElementException):
            raise ChuangYuAntiSpider
        self.sleep(1)
        search.clear()
        search.send_keys(self.search)
        self.sleep(1)
        submit.click()

    def calculate_track(self, picture):
        try:
            body = BytesIO()
            picture.save(body, format='JPEG')
            data = api_get_click_position(body.getvalue())
            if len(data['message']['words']) < 5:
                return data['message']['location']
            logger.info('长度有点长，换个验证码')
            self.sleep(1)
            button = self.driver.find_element_by_xpath('//*[@class="geetest_refresh"]')
            button.click()
            self.sleep(1)
            return self.calculate_track(self.get_click_img())
        except:
            logger.warning("验证码后台识别失败，需要重新尝试")
            raise IdentifyMistakes

    def check(self):
        try:
            self.driver.find_element_by_xpath('//*[@class="search_logo_100000"]')
            return True
        except:
            self.driver.find_element_by_xpath('//*[@class="geetest_refresh"]')

    def run(self):
        if self.max_run:
            self.max_run -= 1

            try:
                self.capture_interface()  # 进入验证码接口界面
            except ChuangYuAntiSpider:
                logger.error("创宇验证码反爬")
                return {'status': 2, 'msg': '创宇验证码反爬'}
            except TimeoutException:
                logger.warning("获取验证码界面失败，重新尝试...")
                return self.run()

            logger.info("进入验证码界面...")

            while True:
                try:
                    button = self.waiter.until(EC.element_to_be_clickable((By.XPATH, '//*[@class="geetest_refresh"]')))
                    button.click()
                    self.sleep(1)
                    self.click_test()  # 开启点选测试
                    if self.check():
                        break
                except (IdentifyMistakes, TimeoutException, NoSuchElementException):  # 验证码识别错误
                    return self.run()
                logger.info("刷新验证码")

            logger.info("进入详情页页面...")

            try:
                element = self.driver.find_element_by_xpath('//*[@class="search_list_item db"][1]')
                if element.is_enabled():
                    return {'status': 1, 'msg': 'Success',
                            'url': element.get_attribute('href'),
                            'Cookie': self.driver.get_cookies()}
            except (TimeoutException, NoSuchElementException):
                pass
            logger.info("未查询到公司记录...")
            return {'status': 0, 'msg': '未查询到 {} 记录'.format(self.search)}

        else:
            logger.info("达到最大尝试次数，结束程序")
            return {'status': 0, 'msg': '数据获取失败-页面阻塞，达到最大尝试次数，结束程序'}


if __name__ == '__main__':
    gongSh = GongSh('武汉数博科技', debug=True)
    print(gongSh.run())
