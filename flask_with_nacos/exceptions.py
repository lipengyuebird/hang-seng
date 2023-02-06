from typing import Optional


class ConfigFileException(Exception):

    def __init__(self, info: Optional[str] = None):
        self.info = info
