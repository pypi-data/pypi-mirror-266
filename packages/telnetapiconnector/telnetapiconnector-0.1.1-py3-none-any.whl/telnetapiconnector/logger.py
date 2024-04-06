import logging
import re
import sys


class SensitiveFormatter(logging.Formatter):
    """Formatter that removes sensitive information."""

    @staticmethod
    def _filter(s):
        # filter user:password combination in urls
        s = re.sub(r'://(.*?)@', r'://', s)

        # filter passwords in dict prints
        matches = re.findall(r'(?:pswd|password)[\'\"]:\s[\'\"](.*?)[\'\"][,}]', s)
        for match in matches:
            s = s.replace(match, '*' * len(match))

        return s

    def format(self, record):
        original = logging.Formatter.format(self, record)
        return self._filter(original)


logger = logging.getLogger('TNAPIconnector')
stdout_handler = logging.StreamHandler(stream=sys.stdout)
stdout_handler.setFormatter(SensitiveFormatter(fmt='%(asctime)s [%(name)s/%(module)s] [%(levelname)s] %(message)s'))
logger.addHandler(stdout_handler)
logger.propagate = False

