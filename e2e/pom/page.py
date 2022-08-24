"""Top-level components for modeling a web page directly."""

from typing import List
from typing import Optional
import contextlib
import logging

from selenium.webdriver.remote.webdriver import WebDriver
from waiter import wait

from e2e.common import util

from . import base
from . import dom
from . import exceptions
from . import locators


LOGGER = logging.getLogger(__name__)


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
        driver: Optional[WebDriver] = None,
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

    @contextlib.contextmanager
    def expect_transition(
        self, timeout_sec: float = 5.0, expected_url: Optional[str] = None
    ) -> None:
        """Waits for a page transition to occur.

        Used as a context manager to clarify which actions should trigger the
        page transition. If the actions do not result in the expected page
        navigation, then an error will be raised.

        Args:
            timeout_sec: How long to wait for a page transition, in seconds
            expected_url: Optionally specify an exact URL to wait on. If not
                specified, simply waits for any URL change.

        Example::
            with page.expect_transition():
                page.nav_button.click()

        Raises:
            e2e.pom.exceptions.TimeoutError: If the expected page transition
                does not occur within the given time.
        """
        original_url = self.driver.current_url
        LOGGER.info('Expecting next action to navigate away from "%s"', original_url)
        yield
        for _ in wait(0.1, timeout_sec):
            last_url = self.driver.current_url
            if expected_url:
                if last_url == expected_url:
                    break
            elif last_url != original_url:
                break
        else:
            if last_url == original_url:
                msg = f'Timed out waiting for page transition; never changed from "{original_url}"'
            elif expected_url:
                msg = f'Timed out waiting for page to transition to "{expected_url}": was instead "{last_url}"'
            raise exceptions.TimeoutError(msg)
