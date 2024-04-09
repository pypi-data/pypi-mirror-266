import logging
import re


class TokenFilter(logging.Filter):
    def filter(self, record):
        record.msg = re.sub(r"appid=?\S+", "appid=...", str(record.msg))
        return True
