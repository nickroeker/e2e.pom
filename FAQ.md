# FAQ

## Header

### Where is the equivalent to `By.ID`? `By.TAG_NAME`? `By.LINK_TEXT`?

These are just shortcuts to a more complete CSS Selector or XPath.

If you are designing selectors, I would highly recommend these two resources
(I always have them open!):

- [CSS Selectors (w3Schools)](https://www.w3schools.com/cssref/css_selectors.asp)
- [XPath Cheatsheet](https://devhints.io/xpath)

### I keep getting `StaleElementReferenceError`, what's wrong?

This means the DOM is changing while you are interacting with it. You likely
need to wait for something in the UI to change or stabilize.

If this is because something is loading and you have no way to tell that it's
not done loading (e.g. a spinner), ask your development team to provide such
an indicator. Your users will appreciate it, and you can use it in automation.
For this, you would use `wait_for_not_visible()`.

### I'm making models, but it requires so many classes. Why?

This is probably a reflection of a complex UI. A UI with many regions and
components will naturally have many classes to model all those regions and
components.

The model detail & compelxity will reflect that of the page being modelled.

### I don't see a way to do/access `WebElement.thing`. What now?

If you normally have access to something on a `WebElement` that can't be done
in `e2e.pom`, this is a bug. Please file an issue and we'll get support for it
ASAP!

### I really need a `WebElement`. How can I get one?

If you use a framework or other thing that needs direct access to Selenium's
`WebElement`, you can access it via `ElementReference.proxy`. You can get
`ElementReference`s via a `.get()` on the component/collection.

Note that this will spam your logs with valid warnings as this isn't an
intended use of the framework. If you find you need to do this because of a
missing feature, please file an issue!
