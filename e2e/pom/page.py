"""Top-level components for modeling a web page directly."""

from typing import List
from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver

from e2e.common import util

from . import base
from . import dom
from . import locators


class Page(base.Parentable):
    """Representation of a whole Page in the Page Object Model.

    Unlike other `e2e.pom` components, Pages themselves cannot be directly
    interacted with. They serve mostly as a container for sub-models, and also
    serve as a convenient top-level object to place a WebDriver on.

    Pages also contain extra functionality related to navigation.

    Note:
        `driver` and `parent` may only be specified by keyword for clarity.

    Args:
        url: URL to navigate to via :meth:`~.Page.go_to`.

    Keyword Args:
        driver: Optionally attach a WebDriver. Child elements will use this
            WebDriver in order to be found and interacted with.
        parent: Optional parent. Usually this would be an
            :class:`~e2e.pom.IFrame`.

    """

    def __init__(
        self,
        url: str,
        *,
        parent: Optional[base.Parentable] = None,
        driver: Optional[WebDriver] = None
    ):
        super().__init__(util.fqualname_of(self), parent=parent)
        self._url = url
        self._driver = driver

    # TODO docs
    def find_within(self, locator: locators.Locator) -> List[dom.ElementReference]:
        if not self.parent:
            self.driver.switch_to.default_content()
            children = locator.locate(self.driver)
            return [dom.ElementReference(c, self) for c in children]
        return self.parent.find_within(locator)
