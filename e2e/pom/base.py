"""Base functionality for `e2e.pom`."""

from typing import List
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from e2e import common

from . import exceptions
from . import locators


class Parentable(common.modelling.NamedParentable):  # TODO types.FindsElements
    """Base class implementing auto-stitching parents in a POM class model."""

    parent: Optional["Parentable"] = None
    _driver: Optional[WebDriver] = None

    def __init__(
        self,
        name: str,
        *,
        parent: Optional["Parentable"] = None,
        driver: Optional[WebDriver] = None,
    ):
        super().__init__(name, parent=parent)
        self._driver = driver

    @property
    def driver(self) -> WebDriver:
        """Returns the driver attached to this element or its parent chain."""
        if self._driver:
            return self._driver
        if self.parent:
            return self.parent.driver
        raise exceptions.PomError(
            "Element has neither a parent nor assigned driver: {}".format(self)
        )
