# Changelog for `potoroo`

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog], and this project adheres to
[Semantic Versioning].

[Keep a Changelog]: https://keepachangelog.com/en/1.0.0/
[Semantic Versioning]: https://semver.org/


## [Unreleased](https://github.com/bbugyi200/potoroo/compare/0.6.0...HEAD)

No notable changes have been made.


## [0.6.0](https://github.com/bbugyi200/potoroo/compare/0.5.0...0.6.0) - 2024-04-05

### Changed

* *BREAKING CHANGE*: Renamed `get_by_tag()` to `get_by_query()`.
* *BREAKING CHANGE*: Renamed `remove_by_tag()` to `remove_by_query()`.
* *BREAKING CHANGE*: Renamed `TaggedRepo` to `QueryRepo`.


## [0.5.0](https://github.com/bbugyi200/potoroo/compare/0.4.1...0.5.0) - 2024-04-03

### Changed

* *BREAKING CHANGE*: Implement `remove_by_tag()` and `remove_by_key()` and
  change remove() to accept item.


## [0.4.1](https://github.com/bbugyi200/potoroo/compare/0.4.0...0.4.1) - 2022-06-04

### Changed

* Improve error handling of default `Repo.update()` implementation.


## [0.4.0](https://github.com/bbugyi200/potoroo/compare/0.3.2...0.4.0) - 2022-06-04

### Added

* *BREAKING CHANGE*: New required abstract `Repo.all()` method.

### Changed

* The `Repo.update()` method now has a default implementation.


## [0.3.2](https://github.com/bbugyi200/potoroo/compare/0.3.1...0.3.2) - 2022-01-17

### Fixed

* Remove `U` generic type variable from `UnitOfWork` class


## [0.3.1](https://github.com/bbugyi200/potoroo/compare/0.3.0...0.3.1) - 2022-01-17

### Added

* Add `potoroo.UnitOfWork` abstract type.


## [0.3.0](https://github.com/bbugyi200/potoroo/compare/0.2.1...0.3.0) - 2022-01-15

### Changed

* *BREAKING CHANGE*: Split `Repository` type into `BasicRepo`, `Repo`, and `TaggedRepo`.


## [0.2.1](https://github.com/bbugyi200/potoroo/compare/0.2.0...0.2.1) - 2022-01-15

### Fixed

* Switch the positions of the type variables used in the `Repository` generic.


## [0.2.0](https://github.com/bbugyi200/potoroo/compare/0.1.0...0.2.0) - 2022-01-15

### Added

* Add `potoroo.Repository` abstract type.

### Miscellaneous

* First _real_ release.


## [0.1.0](https://github.com/bbugyi200/potoroo/releases/tag/0.1.0) - 2022-01-15

### Miscellaneous

* First release.
