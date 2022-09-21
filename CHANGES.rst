Changelog for e2e.pom
=====================

0.1.8 (unreleased)
------------------

- Nothing changed yet.


0.1.7 (2022-09-20)
------------------

- Allow ElementCollection to be a direct parent


0.1.5 (2022-09-20)
------------------

- Better error reporting for issues while finding
- Added DOM presence wait methods


0.1.4 (2022-09-12)
------------------

- [Issue 2] Fix ElementReference naming and parent chain for logging


0.1.3 (2022-08-24)
------------------

- Fix: Missing import


0.1.2 (2022-08-22)
------------------

- Type-hint fixes at the module-level, and a couple method signature fixes
- New way to wait for page transitions: `pom.Page.expect_transition`


0.1.1 (2022-06-26)
------------------

- Packaging and requirements fixes
- Added some left-behind critical missing functions!
- Fixed typos on exception names


0.1.0 (2022-05-09)
------------------

- Exported modelling core to e2e.common, imported and used here
- Fixed some type-hints based on updated mypy versions
- Fixed some issues mypy had detecting types in the package at all
- Updated tags to support Python 3.9, 3.10


0.0.1 (11-19-2020)
------------------

- Initial release! Elements, Collections, IFrames, and Pages.
