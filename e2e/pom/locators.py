"""TODO"""
import abc
from typing import List
from typing import Tuple
from typing import Union

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webdriver import WebElement


class Locator(abc.ABC):
    """A simple shim to the internals of finding objects with Selenium."""

    def __init__(self, method: str, value: str):
        self._method = method
        self._value = value

    @property
    def tuple(self) -> Tuple[str, str]:
        """Returns a locator tuple commonly compatible with the Selenium API."""
        return self._method, self._value

    @abc.abstractmethod
    def locate(self, finder: Union[WebDriver, WebElement]) -> List[WebElement]:
        """Locate DOM elements using the given `finder`.

        `finder` will be either a Selenium ``WebDriver`` or a Selenium
        ``WebElement``, depending on which is necessary to locate the next
        object in the parent chain.

        If a ``WebElement`` is given, found elements must only be returned for
        those found inside of the given element.
        """


class SeleniumLocator(Locator):
    """Locator representing a typical Selenium-style lookup.

    For example, using Selenium's ``By``::

        username_locator = SeleniumLocator(By.ID, 'username')

    Args:
        method: The Selenium lookup scheme, e.g. ``By.ID`` or simply ``'id'``.
        value: The locator value, e.g. ``'username'``.

    """

    def locate(self, finder: Union[WebDriver, WebElement]) -> List[WebElement]:
        """Locate DOM elements using the given `finder`."""
        elements: List[WebElement] = finder.find_elements(*self.tuple)
        return elements


def by_css(css_selector: str) -> SeleniumLocator:
    """Generates a Locator for a regular Selenium CSS locator scheme."""
    return SeleniumLocator("css selector", css_selector)


def by_xpath(xpath: str) -> SeleniumLocator:
    """Generates a Locator for a regular Selenium XPath locator scheme."""
    return SeleniumLocator("xpath", xpath)
