from abc import ABC
from robocorp import browser


class Browser(ABC):
    def __init__(self):
        self.browser = browser
        browser.configure(
                browser_engine="chrome", screenshot="only-on-failure", headless=False, isolated=True, slowmo=1
            )