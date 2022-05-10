"""Representations and models for DOM objects & interaction."""
import logging
from typing import TYPE_CHECKING
from typing import List
from typing import Optional
from typing import TypeVar
from typing import Union

import selenium.common.exceptions as selenium_exceptions
from selenium.webdriver.remote.webdriver import WebElement

from e2e.common import util

from . import locators

LOGGER = logging.getLogger(__name__)

T = TypeVar("T", bound="ElementReference")

if TYPE_CHECKING:
    from .components import Findable


class ElementReference:
    """Representation of a specific element in the DOM.

    An `ElementReference` could be considered the low-level interface to
    Selenium, and thus behaves more similar to its API than `e2e.pom`.

    This is an exact reference, and so it can go "stale" - that is, the element
    it represents may be removed from the page and thus can no longer be
    interacted with or checked in any way.
    """

    def __init__(self, web_element: WebElement, origin: Optional["Findable"] = None):
        self._web_element = web_element
        self._locator = origin

    @property
    def proxy(self) -> WebElement:
        LOGGER.warning("Providing raw WebElement for: %s", self)
        return self._web_element

    def find_within(self, locator: locators.Locator) -> List["ElementReference"]:
        children = locator.locate(self._web_element)
        # TODO: This is an error: self is wrong, maybe this should just return
        # raw WebElements that are wrapped later.
        return [ElementReference(c, self) for c in children]

    # Data methods
    def get_attribute(self, attr: str) -> Union[str, bool, None]:
        return self._web_element.get_attribute(attr)

    def get_text(self) -> str:
        return self._web_element.text

    # State methods
    def is_selected(self) -> bool:
        return self._web_element.is_selected()

    def is_enabled(self) -> bool:
        return self._web_element.is_enabled()

    def is_visible(self) -> bool:
        """Returns whether or not the element reference is visible.

        If the reference has been removed from the DOM, return False.
        """
        try:
            return self._web_element.is_displayed()
        except selenium_exceptions.StaleElementReferenceException:
            return False

    # Interactions
    def click(self) -> None:
        self._web_element.click()

    def clear(self) -> None:
        self._web_element.clear()

    def send_keys(self, keys: str) -> None:
        self._web_element.send_keys(keys)

    def __repr__(self) -> str:
        return "{}({})".format(util.fqualname_of(self), self._web_element.id)

    def __str__(self) -> str:
        return "{} of {}".format(util.fqualname_of(self), self._locator)
