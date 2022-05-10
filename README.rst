e2e.pom - Page Object Modelling for End-to-End Testing
======================================================

Use ``e2e.pom`` to easily create reusable Page Object Models that offer
functionality and error scenarios more naturally than Selenium can.

Extend available locators with plugins like ``e2e.pom.extjs`` for
ExtJS/Sencha Locators, or write your own!

Eliminate iframe-handling in your tests — let the model take care of
where your elements reside. In fact, all elements are guaranteed to be
found within their parent model so you can write unique selectors
without specifying a long ancestry within the selector itself!

All actions are logged with human-friendly labels, with human-friendly
exceptions indicating exactly where things went wrong.

Beta Notice
-----------
``e2e.pom`` is still in **beta**, but the API is expected to be stable. The
project is very open to suggestions and feedback at this stage!

This project follows SemVer. It is expected that the first major release (1.x)
will **not** differ in API functionality much from the alpha/beta track
(0.x).

Python 3.6+ is currently required. No support for 2.x is ever planned since
it is soon to be unsupported. Please feel free to file an issue if you need
support for an earlier Python version and simply cannot upgrade.


Modelling Examples
------------------

Pages and their components are easy to model on a class-member basis.
You do not need to pass around a driver, nor do you need to write
properties or methods. There is no need to override ``__init__``
properly either; just author your static model and be done with it!

.. code:: py

   class LoginForm(pom.Region):
       username_field = pom.Element("Username").by_css('.username')
       password_field = pom.Element("Password").by_css('.password')
       login_button = pom.Element("Login btn").by_css('#login-submit')

   class LoginPage(pom.Page):
       login_form = LoginForm("Login form").by_css('.login')

   # ...

   login_pg = LoginPage("https://my-login-service.local:8443", driver)
   login_pg.login_form.wait_for_visible()
   login_pg.login_form.username_field.set_text('Admin1')
   login_pg.login_form.password_field.set_text('Sup3rS3cret!')
   login_pg.login_form.login_button.click()

IFrame Handling
~~~~~~~~~~~~~~~

Handling iframes with Selenium is incredibly annoying. ``e2e.pom``
provides a special component that you can use as a hidden parent so that
test authors do not need to be concerned about the iframe at all.

.. code:: py

   class LoginForm(pom.Region):
       # Same as Example Model above

   class LoginPage(pom.Page):
       # Hide the iframe POM component so the test doesn't need to be aware by
       # overriding the parent of the Form.
       _login_service_iframe = pom.IFrame("LoginService iframe").by_css('iframe#login-service')
       login_form = LoginForm("Login form").by_css('.login', parent=_login_service_iframe)

   # Use exactly as before, like the iframe isn't even there!
   login_pg.login_form.wait_for_visible()

The POM framework will then handle switching to the correct iframes.
Even if a service *becomes* resident within an iframe that was otherwise
inline before, you only need to change the *model* and not the test
code!

In addition, features like ``is_visible()`` are mindful of iframes. That
is, unlike using Selenium directly, if the iframe is not displayed then
``e2e.api`` counts all of its children as invisible.

Hidden Regions
~~~~~~~~~~~~~~

Like the above case for IFrames, you may want to hide a certain part of
the model but otherwise use it as a parent to other components. This is
often useful for ensuring elements are found within a certain part of
the page, but would be too verbose to specify in every test.

.. code:: py

   class ServicePage(pom.Page):
       _nav_bar = pom.Region("Navigation bar").by_css('.upper-nav-container')
       settings_button = pom.Element("Setting btn").by_css('.gear-icon')

   # You can now do this...
   service_pg.settings_button.click()

   # Instead of having to do this
   service_pg.navigation_bar.settings_button.click()

This is especially useful when you have, like in the above example,
multiple elements that use ``.gear-icon`` but are obviously referring to
one particular instance of it. If it is beneficial to the clarity of
your model though, you may want to *not* hide the parent since the
increased verbosity may make your test’s actions more clear to others.

Interacting with Elements
-------------------------

While some available methods are similar to Selenium’s API, they have
differing requirements and behaviours.

For example, the concept of “visibility” is now more user-friendly.
Whether an element is *visible* to the user depends not only on the
display info of the element, but whether the element exists at all. With
Selenium, entirely different code is required to handle that difference!
With ``e2e.pom``, it is *just* the visiblility functions. This allows
product developers to use techniques like DOM caching without needing to
change the test code. This way, ``e2e.pom`` is checking *user intent*
rather than *implementation details*.

.. code:: py

   # Case 1: With Selenium, element not in DOM. Can also assert NoSuchElement was raised.
   assert driver.find_elements_by_xpath(...) == []

   # Case 2: With Selenium, element in DOM
   assert driver.find_elements_by_xpath(...).is_displayed()

   # With happy-path-only POM frameworks (not e2e.pom)
   try:
       assert modelled_element.is_displayed()
   except NoSuchElementException:
       pass

   # With e2e.pom (works for both above cases)
   assert modelled_element.is_visible()

*Nothing* happens until you call a method on an element. This is to give
clarity as to when the finding, attribute checking, and interaction
takes place within a test.

.. code:: py

   # Selenium: All of these do something with the driver, even the properties!
   element = driver.find_element_by_css_selector(...)
   element.text
   element.is_displayed()
   element.click()
   element.clear() and element.send_keys("some text")

   # e2e.pom: Consistent API. Methods == driver actions.
   element.get_text()
   element.is_visible()
   element.click()
   element.set_text("some text")

All user-like interaction methods require visibility of the element. If
the element is not visible, a user cannot interact with it. Exceptions
will be raised with the exact details (e.g. if it was because a parent
could not be located, the exception will state this).

Sets of Elements
----------------

Sometimes you are intentionally referring to a group of similar
elements, like rows of a particular type. You can’t use a
``pom.Element`` for this because they require *uniquely* finding an
element. In this case, you can use ``pom.ElementCollection``.

Rich Visibility
---------------

To-do.

Using Locators Provided by Third-Party Plugins
----------------------------------------------

In certain projects, alternative locator methods may be available that
are more deterministic of exact elements.

A first-party example of this, ``e2e.pom.extjs``, provides locators for
pages built with ExtJS/Sencha.

This extensibility has a few drawbacks to be aware of:

-  The generic ``by(...)`` must be used instead of something like
   ``by_css(...)``
-  Many setups will fail to type-check or auto-complete this correctly.

Using it is very easy though! Just ensure it is installed, then use the
provided ``Locator`` class directly in the ``by()`` construction.

.. code:: py

   from e2e import pom
   from e2e.pom import extjs

   class ServicePage(pom.Page):
       alert_popup = pom.Element("Alert").by(extjs.Locator('panel[title=Alert]'))

Developing Locator Extensions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Please use ``e2e.pom.extjs`` as an implementation guide.

The following are recommended:

-  The extension locator class should be called ``Locator`` where
   possible.
-  ``find_within`` is the only method needing implementation. It will be
   passed *either* a ``WebDriver`` or a ``WebElement``. For the
   ``WebElement``, you *must* assure that anything returned by your
   Locator is within the given ``WebElement``.
-  Don’t forget to register the entrypoint!

Pytest Hooks & Fixtures (BETA)
------------------------------

*Note:* This feature is under development and *will* change. Feedback is
much appreciated!

A information-providing fixture is provided for dumping info useful in
test failure analysis.

You must register the drivers you use with this fixture. We recognize
users will have their own ways of managing drivers, so this is the best
way currently.

.. code:: py

   def test_my_thing(e2e_pom_dumper: pom.fixtures.DumperFixture):
       my_driver = ...  # However you get this
       e2e_pom_dumper.register_driver(my_driver)
       # Now you can use the driver!

After that, the following features are provided:

-  On test failure, two DOMs are dumped to HTML files:

   -  The current frame/iframe at the time of failure (if not the root
      frame)
   -  The root frame

-  A screenshot is taken at the outermost/root frame

Performance Considerations
--------------------------

Certain features like Collections as parents can result in a lot of
Selenium requests being issued. If you test against a busy Selenium
Grid, this can definitely slow things down!

I do not normally recommend the below workarounds (because they bypass
some significant benefits of the framwork), but you may find them
necessary in your case.

1. Avoid a ``pom.Collection`` parent if it represents many elements
   (e.g. rows in a large table). Every found element for the collection
   is searched for the next child.
2. Reduce POM depth where possible. Since each child causes a Selenium
   find request on interaction, reducing the size of that parentage can
   speed things up.

For the first case, this can be easy to work around with a dynamic model
if you are targeting a particular item.

.. code:: py


   class MyTable(pom.Container):

       rows = pom.Collection('Rows').by_css('tr')

       def row_by_title(self, title: str):
           label = f'Row by title [{title}]'
           xpath = f'.//td[text()="{title}]/ancestor::tr"'
           # Do this IF Selenium performance isn't critical to you (most cases)
           return pom.Element(label).by_xpath(xpath, parent=rows)
           # Do this IF and ONLY IF Selenium performance is very important to you
           return pom.Element(label).by_xpath(xpath)

Note how ``rows`` is on the model directly, but also used as a parent
override in the method. However, skipping ``rows`` as a parent means we
can forego some more detailed information on failure while making less
Selenium calls.

Making Richer Models
--------------------

Generic type information can be passed regarding the type of located
elements.

This is especially useful for ``pom.ElementCollection``\ s. For example,
you may want to have an ``icon`` property modelled on each dropdown item
returned from a collection. This is normally modelled by a Findable
component (e.g. ``pom.Container`` or ``pom.Element``), but these cannot
be used for *found* elements (those returned by
``pom.ElementCollection.get()``). Enter, generics.

On construction of *any* findable POM type, you can specify the concrete
type returned by ``findable.get()`` or acted on via operations like
``findable.click()``. By default, this is a
``pom.dom.ElementReference``, but you may extend it to provide more
functionality.

# TODO: assert Reference parents actually work!

.. code:: py

   class Dropdown(pom.Container):

       class IconItem(pom.dom.ElementReference):
           icon = pom.Element("Icon").by_css(".option-icon")

       items = pom.ElementCollection("Dropdown items", IconItem).by_css("option")

   first_item = ...dropdown.items.get()[0]
   assert 'gear-icon' in first_item.icon.get_attribute('class')

The type of ``items`` is now a ``pom.ElementCollection<IconItem>``. If
it was not specified, it would be a
``pom.ElementCollection<dom.ElementReference>``.

This works because while an ElementReference is not “Findable”, it *is*
“Parentable”. That is, it can be a parent, and thus contain other
modelled children.

In the future, a pom.HybridElement may exist that can be used to
represent these items both as a Findable and a Found object to avoid
code duplication.

Basically, a rich interface is what you write.

