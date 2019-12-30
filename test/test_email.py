from minitools import Emailer

if __name__ == '__main__':
    ems = Emailer('smtp.qq.com', 'xxxxxxxxx@qq.com', 'xxxxxxxxxxxx', receiver='972542655@qq.com')
    ems.send("test", "hello world")
