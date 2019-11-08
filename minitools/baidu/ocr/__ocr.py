import json

from aip import AipOcr

__all__ = 'BaiDuOcr',


class BaiDuOcr:

    def __init__(self, *account):
        self.client = AipOcr(*(account or ('17723391', 'ecQZ3dsGp5pQ2eguH9RbiveH', 'jVGDBIyDVRfzL3CV7G2LFUyzbgu7yxc4')))

    def set_account(self, *account):
        self.client = AipOcr(*account)

    def webImage2word(self, imgBody):
        return json.dumps(self.client.webImage(imgBody), ensure_ascii=False)
