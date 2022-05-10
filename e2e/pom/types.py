from typing import TYPE_CHECKING
from typing import List

from selenium.webdriver.remote.webdriver import WebElement
from typing_extensions import Protocol

if TYPE_CHECKING:
    from . import locators


class FindsElements(Protocol):
    """Duck protocol for e2e.pom classes capabale of locating elements."""

    def _find_within(self, locator: "locators.Locator") -> List[WebElement]:
        """Docs"""
        ...
