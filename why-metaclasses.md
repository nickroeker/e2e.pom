# Why use Metaclasses?

It's easy to answer this with the missteps of other methods attempted over the
years.

The problem that is to be solved is ensuring that we can set the parent element
automagically if one is not specified, without clobbering an explicitly set
parent.

It is beneificial to solve this problem in a way that static analysis tools
(e.g. _pylint_, _flake8_) and type checkers (e.g. _mypy_, IDE completion) do
not get confused or mislead a user regarding the modeling framework.

## Do nothing: `__init__`

On the upside, this completely works. However, it's less of a framework and
more of a design standard, which leads to inconsistencies over time.

```python
class LoginForm(pom.Region):

    def __init__(self, name):
        super().__init__(name)
        self.username_field = pom.Element("Username").by_css('.username', parent=self)
        self.password_field = pom.Element("Password").by_css('.password', parent=self)

class LoginPage(pom.Page):

    def __init__(self, url):
        super().__init__(url)
        self._main_content = pom.Element("Main content").by_css('#login-service', parent=self)
        self.login_form = LoginForm("Login form").by_css('.login', parent=self._main_content)
```

All the `super().__init__(...)` and `parent=self` boilerplate gets annoying to
some. An upside however is that it's obvious that you can always specify a
`parent`, be it `self` or some other thing (e.g. `_main_content` hidden parent
above).

**Downsides**:

- The model cannot be accessed without an instance, though it is inherently
  static in reality.
- Room for improvement on repetition and doing things for the user.

## Re-assign parents on construction: `__init__`

Unsurprisingly, type checkers lose their mind on this one. There's too much
`getattr` and `setattr` involved, and type information tends to get lost or
become overly complicated.

Additionally, this requires users to remember to call `super().__init__(...)`
if they redefine the constructor. While this is best practice anyways, it's not
strictly required and the absense would kill the parent chain at the custom
model.

Note that since there are complexities of recursion otherwise, this has the
same limitation as `__get__` (see below) regarding hidden elements.

```python
class LoginForm(pom.Region):
    username_field = pom.Element("Username").by_css('.username')
    password_field = pom.Element("Password").by_css('.password')

class LoginPage(pom.Page):

    def __init__(self, url, custom_param):
        super().__init__(url)
        self.custom = custom_param

    _main_content = pom.Element("Main content").by_css('#login-service')

    @property
    def login_form(self):
        return LoginForm("Login form").by_css('.login', parent=self._main_content)
```

**Downsides**:

- Some of the model can be accessed statically, but not all of it. This is
  strange and confusing.
- Echoing the above, the actual modeling can be inconsistent.
- Unnaturally, users have to be careful when overriding `__init__`.

## Re-assign on attribute lookup: `__getattribute__`

A more familiar and often-used magic method, `__getattribute__` nearly provides
a workable interface. Most tools understand it out of the box. However, it puts
the onus of mapping the parent on the owning container rather than the child.

This logic thus fires for _all_ attributes, whether they are `Element`s we need
to check the parent on or not. And it fires _all the time_. Performance is not
the main concern of `e2e.pom`, but some would look down on this.

We also only have access to an attribute `name` via this method. This
requires yet more use of `getattr` and `setattr`, and we once again have a hard
time with type information.

In general the name is simply not enough information, so no example is provided
for this method.

**Downsides**:

- Poor type-hinting (users loose most IDE auto-completion, etc., especially for
  accessing various parts of their model).
- Expensive operation, always returns new instances of children.

## Re-assign on dotted reference: `__get__`

A more "magical" method than the previous, this fixes some of the issues we
would otherwise have. This is defined on the `Element` types, so the magic is
only performed where it needs to be. Type-hinting and tools analysis is also
better supported, surprisingly. We have some relatively nice correlations we
can make.

A very large problem exists though: You cannot have "hidden" parents within
your model. These terminate the parent chain prematurely and silently, which in
my opinion is a very large bug.

A workaround for this is to model anything that needs the hidden parent as a
`@property`, so that the hidden is accessed as `self._hidden` (effectively
working around the issue by dotting through `self`). Honestly, this is
downright confusing as a user, and you'd have to read documentation to realize
you even have a problem that needs "fixing".

Another downside (reflected in an implementation of this protocol) is that
instances of a model are not necessarily fully correct at runtime. Parenting is
only stitched together as you dot your way though a model (i.e.
`page.region.element`). That is, it has the same problem as `__getattribute__`
-- it's faked to work instead of being an accurate model.

```python
class LoginForm(pom.Region):
    username_field = pom.Element("Username").by_css('.username')
    password_field = pom.Element("Password").by_css('.password')

class LoginPage(pom.Page):
    _main_content = pom.Element("Main content").by_css('#login-service')

    @property
    def login_form(self):
        return LoginForm("Login form").by_css('.login', parent=self._main_content)
```

**Downsides**:

- Some of the model can be accessed statically, but not all of it. This is
  strange and confusing.
- Echoing the above, the actual modeling can be inconsistent.
- Buggy behaviour is extremely hard to notice and/or diagnose for hidden parts
  of the parent chain.

## Metaclass

Though a more esoteric feature of Python, a metaclass is extremely useful here.

- We're separating how the model is constructed from how the instances operate.
  This is incredibly valuable, as it implies all following good points.
- An instance of a model is correct, complete, and behaves as expected after
  construction.
  - This is not true of other methods, since their behaviour isn't via true
    object members, and is constantly re-calculated and re-stitched.
  - Less prone to bugs since the model is complete after instantiation, no
    further magic necessary.
- Users need not worry about overriding `__init__`, `__new__`, `__get__`, etc.
  themselves, nor necessarily having to call the `super` methods to keep the
  framework working.
- The model pieces are made to be read-only (i.e. `@property`) to minimize the
  temptation to introduce unexpected behaviour. It is a model, after all.
- This exposes the most minimal API with the most functionality.

This provides for extra extensibility in the future as well, such as arguments
for the class construction itself. This could be used on `pom.Region`s for
example, to specify a default locator or name.

A potential downside is a misleading type-inference. In `e2e.pom`, this doesn't
appear to be a problem because the metaclass is making properties which return
the same instances modeled on the classes (but augmented), so type checkers and
docs generators seem to do more or less the correct thing. It _is_ a problem if
you think you can access something like `LoginForm.username_field` -- this is
now actually a `property` object at the class level and does not return a POM
construct. This can likely be fixed by a using custom descriptor protocol to
replace `property`.

```python
class LoginForm(pom.Region):
    username_field = pom.Element("Username").by_css('.username')
    password_field = pom.Element("Password").by_css('.password')

class LoginPage(pom.Page):
    _main_content = pom.Element("Main content").by_css('#login-service')
    login_form = LoginForm("Login form").by_css('.login', parent=_main_content)
```

**Downsides**:

- Potentially confusing that `SomeClass.some_pom_thing` is a `property` object.
- It took way too many hours to arrive at this solution.
