"""Various components provided by `e2e.pom` for making Page Object Models."""

import itertools
import logging
from typing import Any
from typing import List
from typing import Optional
from typing import TypeVar

from waiter import wait

from . import base
from . import dom
from . import exceptions
from . import locators

T = TypeVar("T", bound="Findable")
# T_R = TypeVar("T_R", bound=dom.ElementReference)

LOGGER = logging.getLogger(__name__)


# TODO: I thought this was a collection, so should probably move to Collection
class Findable(base.Parentable):
    """TODO"""

    locator: Optional[locators.Locator] = None

    def by_css(self: T, css_selector: str) -> T:
        """Sets the scheme to find this element to the given CSS Selector."""
        self.locator = locators.by_css(css_selector)
        return self

    def by_xpath(self: T, xpath: str) -> T:
        """Sets the scheme to find this element to the given XPath."""
        self.locator = locators.by_xpath(xpath)
        return self

    # # TODO
    # def _find_all(self) -> List[dom.ElementReference]:
    #     """Find this element within its parent, and that within its own, etc.

    #     Uses the parent chain to incrementally decrease the scope of elements
    #     which can be found.
    #     """
    #     pass
    #     # return self.

    #     # parents = self.parent_chain
    #     # parents.reverse()
    #     # for p in parents:
    #     #     p._find()

    # TODO, maybe make ABC?
    # TODO: Rename to find_all if both Singular and Collections use it?
    def _find_all(self) -> List[dom.ElementReference]:
        """Find this element within its parent, and that within its own, etc.

        Uses the parent chain to incrementally decrease the scope of elements
        which can be found.
        """
        if not self.locator:
            raise exceptions.PomError(
                "Cannot find element (no attached locator): {}".format(self)
            )
        if self.parent:
            # TODO does this return multiple?
            # TODO reveal_type(self.parent)
            return self.parent.find_within(self.locator)
        # TODO does this logic belong here?
        children = self.locator.locate(self.driver)
        return [dom.ElementReference(c, self) for c in children]

    # TODO: ABC method, but can be list or singular, weird
    def find(self) -> Any:
        pass

    def _find_within(self, locator: locators.Locator) -> List[dom.ElementReference]:
        # TODO: this is singular or list, not always list
        self_refs: List[dom.ElementReference] = self.find()
        children = itertools.chain.from_iterable(
            locator.locate(r.proxy) for r in self_refs
        )
        # TODO: This is an error: self if wrong, maybe this should just return
        # raw WebElements that are wrapped later.
        return [dom.ElementReference(c, self) for c in children]


class Container(Findable):
    """A non-interactable container for other POM constructs.

    Generally this is a form, region, panel, etc. of some portion of your page
    which is sensible or convenient to model as a parent of other components.

    Note:
        `driver` and `parent` may only be specified by keyword for clarity.

    Args:
        name: Human-friendly name used for logging, string representations.

    Keyword Args:
        driver: Optionally attach a WebDriver. This element and its children
            will use this WebDriver directly in order to be found and interacted
            with.
        parent: Optional parent. Specifying a parent will limit the search for
            this element to within the element(s) found by the parent.

    """

    # TODO
    def _find(self, locator: locators.Locator) -> Any:
        pass

    def find_within(self, locator: locators.Locator) -> List[dom.ElementReference]:
        # TODO: See if can merge impl. with Singular & Collections
        self_ref = self.find()
        children = locator.locate(self_ref._web_element)
        # TODO: This is an error: self is wrong, maybe this should just return
        # raw WebElements that are wrapped later.
        return [dom.ElementReference(c, self) for c in children]

    # TODO
    def find(self) -> dom.ElementReference:
        """Finds a unique reference matching this model in the DOM."""
        if not self.locator:
            raise exceptions.PomError(
                "Cannot find element (no attached locator): {}".format(self)
            )
        if self.parent:
            found_refs = self.parent.find_within(self.locator)
        else:
            found_refs = [
                dom.ElementReference(we, self)
                for we in self.locator.locate(self.driver)
            ]
        if not found_refs:
            raise exceptions.ElementNotFoundError
        if len(found_refs) > 1:
            raise exceptions.ElementNotUniqueError
        return found_refs[0]

    def is_visible(self, do_not_log: bool = False) -> bool:
        """Returns whether or not this element is deeply visible."""
        # TODO: deeper visibility check (iframe)
        if not do_not_log:
            LOGGER.info("Checking visibility of %s", self)
        try:
            return self.find().is_visible()
        except exceptions.ElementNotFoundError:
            return False

    def is_in_dom(self) -> bool:
        """Returns whether or not this element can be found right now."""
        LOGGER.info("Checking presence of %s", self)
        try:
            self.find()
        except exceptions.ElementNotFoundError:
            return False
        return True

    def is_selected(self) -> bool:
        return self.find().is_selected()

    def is_enabled(self) -> bool:
        return self.find().is_enabled()

    def get_attribute(self, attr: str) -> None:
        """Get an attribute from the DOM object found by this model."""
        LOGGER.info('Fetching attribute "%s" from %s', attr, self)
        return self.find().get_attribute(attr)

    def get_text(self) -> None:
        """Get the inner text of this element."""
        LOGGER.info("Fetching text from %s", self)
        return self.find().get_text()

    def wait_for_visible(self, timeout_sec: float = 5.0) -> None:
        LOGGER.info("Waiting for visibility of %s", self)
        for _ in wait(0.1, timeout_sec):
            if self.is_visible(do_not_log=True):
                break
        else:
            raise exceptions.TimeoutError(
                f"Timed out after {timeout_sec}s waiting for visibility of {self}"
            )

    def wait_for_invisible(self, timeout_sec: float = 5.0) -> None:
        LOGGER.info("Waiting for invisibility of %s", self)
        for _ in wait(0.1, timeout_sec):
            if not self.is_visible(do_not_log=True):
                break
        else:
            raise exceptions.TimeoutError(
                f"Timed out after {timeout_sec}s waiting for invisibility of {self}"
            )


class IFrame(Container):
    """A special context-switching representation of an <iframe>.

    Children of this modelled element will automatically be searched within
    the context of the iframe -- your model-using code then never needs to
    switch the Selenium frame context.

    Args:
        name: Human-friendly name used for logging, string representations.

    Keyword Args:
        driver: Optionally attach a WebDriver. This element and its children
            will use this WebDriver directly in order to be found and interacted
            with.
        parent: Optional parent. Specifying a parent will limit the search for
            this element to within the element(s) found by the parent.

    """

    def find_within(self, locator: locators.Locator) -> List[dom.ElementReference]:
        # TODO: See if can merge impl. with Singular & Collections
        self_ref = self.find()
        self.driver.switch_to.frame(self_ref._web_element)
        children = locator.locate(self.driver)
        # TODO: This is an error: self is wrong, maybe this should just return
        # raw WebElements that are wrapped later.
        return [dom.ElementReference(c, self) for c in children]


# TODO: Findable[dom.T]
class ElementCollection(Findable):

    # TODO
    def find_within(self, locator: locators.Locator) -> List[dom.ElementReference]:
        # found_refs = locator.locate(ctx)
        self_refs = self._find_all()
        child_refs: List[dom.ElementReference] = []
        for ref in self_refs:
            child_refs.extend(ref.find_within(locator))

    # TODO
    def find(self) -> List[dom.ElementReference]:
        """Finds all references matching this model in the DOM."""
        found_refs = self._find_all()
        return found_refs


# TODO: ? Container[dom.T]
class Element(Container):
    """An interactable element which may contain further POM constructs.

    Generally this is a button, text field, or other interactable portion of
    your page. A good test of whether something should be an `Element` is if it
    reacts to user input in any way.

    Note:
        `driver` and `parent` may only be specified by keyword for clarity.

    Args:
        name: Human-friendly name used for logging, string representations.

    Keyword Args:
        driver: Optionally attach a WebDriver. This element and its children
            will use this WebDriver in order to be found and interacted with.
        parent: Optional parent. Specifying a parent will limit the search for
            this element to within the element(s) found by the parent.

    """

    def click(self) -> None:
        """Clicks the DOM item matching this element."""
        LOGGER.info("Clicking on %s", self)
        self.find().click()

    def clear_text(self) -> None:
        """Clear the text from this element."""
        LOGGER.info("Clearing text from %s", self)
        self.find().clear()

    def send_keys(self, keys: str, do_not_log: bool = False) -> None:
        """Send keys to the element, a composition of text and/or special keys.

        Args:
            keys: The string and/or special keys to send to the element
            do_not_log: If set to True, disables logging (e.g. for passwords)
        """
        if not do_not_log:
            LOGGER.info('Sending text to %s: "%s"', self, keys)
        self.find().send_keys(keys)

    def set_text(self, txt: str, do_not_log: bool = False) -> None:
        """Clears the field, then sets the text to the given value.

        Args:
            keys: The string and/or special keys to send to the element
            do_not_log: If set to True, disables logging (e.g. for passwords)"""
        if not do_not_log:
            LOGGER.info('Setting text of %s: "%s"', self, txt)
        self.find().clear()
        self.find().send_keys(txt)
