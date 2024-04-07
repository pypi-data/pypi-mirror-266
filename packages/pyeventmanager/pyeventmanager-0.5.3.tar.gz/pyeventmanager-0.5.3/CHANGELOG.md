# Changelog

## [0.5.3](https://github.com/JeordyR/PyEventManager/compare/v0.5.2...v0.5.3) (2024-04-06)


### Bug Fixes

* remove prints and a few debug logs from batch listener ([37999a3](https://github.com/JeordyR/PyEventManager/commit/37999a3c5d83884d1ecc11157448fb251d9752c2))

## [0.5.2](https://github.com/JeordyR/PyEventManager/compare/v0.5.1...v0.5.2) (2024-04-06)


### Bug Fixes

* fix batch to handle 0 batch_count, EventManager methods to classmethods, schedule listener to daemon ([c503205](https://github.com/JeordyR/PyEventManager/commit/c5032051d44e561734a4797d43cde1f3a07be3eb))

## [0.5.1](https://github.com/JeordyR/PyEventManager/compare/v0.5.0...v0.5.1) (2024-04-02)


### Bug Fixes

* update interfaces to use Protocol instead of abc ([d028702](https://github.com/JeordyR/PyEventManager/commit/d0287024b52ef6f13ebb2a7b560b4e23496316a3))

## [0.5.0](https://github.com/JeordyR/PyEventManager/compare/v0.4.1...v1.0.0) (2024-04-01)


### ⚠ BREAKING CHANGES

* Added support for responses using Futures, changed EventManager to be static implementation.

### Features

* Added support for responses using Futures, changed EventManager to be static implementation. ([2f27db5](https://github.com/JeordyR/PyEventManager/commit/2f27db5f92fe5a827071a69112893ba09ea69474))

## [0.4.1](https://github.com/JeordyR/PyEventManager/compare/v0.4.0...v0.4.1) (2024-03-22)


### Bug Fixes

* fix queues not storing and retrieving data as expected ([74d74c0](https://github.com/JeordyR/PyEventManager/commit/74d74c097762ad4ea296ccd89350ecdbf00d981e))

## [0.4.0](https://github.com/JeordyR/PyEventManager/compare/v0.3.0...v0.4.0) (2024-03-22)


### Features

* rework back to using straight Process and Thread ([1c53443](https://github.com/JeordyR/PyEventManager/commit/1c53443d7f205d0b178ce35413742fe5bf48c44f))

## [0.3.0](https://github.com/JeordyR/PyEventManager/compare/v0.2.3...v0.3.0) (2024-03-22)


### Features

* updated system to use concurrent.futures for concurrency ([cdfab2d](https://github.com/JeordyR/PyEventManager/commit/cdfab2dd49d625c4caad2030f2329a1eadf1fb94))

## [0.2.3](https://github.com/JeordyR/PyEventManager/compare/v0.2.2...v0.2.3) (2024-03-22)


### Bug Fixes

* set Process listeners to run non-daemon if already in a daemon process ([8a1fc77](https://github.com/JeordyR/PyEventManager/commit/8a1fc773d574189530c8d5eae12d218bd2e8473a))

## [0.2.2](https://github.com/JeordyR/PyEventManager/compare/v0.2.1...v0.2.2) (2024-03-22)


### Bug Fixes

* fix instantiation of multiprocessing Queue to include ctx ([5e43b90](https://github.com/JeordyR/PyEventManager/commit/5e43b9009e382202c98f63ea86b2c505d46a200c))

## [0.2.1](https://github.com/JeordyR/PyEventManager/compare/v0.2.0...v0.2.1) (2024-03-22)


### Bug Fixes

* fix instantiation of multiprocessing Queue to include ctx ([2d865cd](https://github.com/JeordyR/PyEventManager/commit/2d865cd44813f016b86006ab5bd3643ff7e9ff63))

## [0.2.0](https://github.com/JeordyR/PyEventManager/compare/v0.1.3...v0.2.0) (2024-03-20)


### Features

* Add ability to stop scheduled listeners. ([b672fde](https://github.com/JeordyR/PyEventManager/commit/b672fde1980e7dddf5c85ec1f24c7712f209006c))
* Allow arbitrary input to all listener types excent BatchListeners ([54e2ead](https://github.com/JeordyR/PyEventManager/commit/54e2eadf8bb1c09a506b1c162d182f41a290af3a))


### Bug Fixes

* Update package links ([05847ef](https://github.com/JeordyR/PyEventManager/commit/05847efad7f33953ecd91b8fdec86a3bb0f43a45))

## [0.1.3](https://github.com/JeordyR/PyEventManager/compare/v0.1.2...v0.1.3) (2024-03-19)


### Bug Fixes

* try another project name ([38b82c9](https://github.com/JeordyR/PyEventManager/commit/38b82c9fed604f85c8aa1a76afeb472b9689c57c))

## [0.1.2](https://github.com/JeordyR/PyEventManager/compare/v0.1.1...v0.1.2) (2024-03-19)


### Bug Fixes

* try another project name ([7ecd4ad](https://github.com/JeordyR/PyEventManager/commit/7ecd4ad99410cf335fc8943cfdf9cd9608a09610))

## [0.1.1](https://github.com/JeordyR/PyEventManager/compare/v0.1.0...v0.1.1) (2024-03-19)


### Bug Fixes

* use a different package name ([ca77011](https://github.com/JeordyR/PyEventManager/commit/ca77011cc3655cce684a0f6bba3f6ee342a3c3cd))

## 0.1.0 (2024-03-19)


### Features

* Initial commit. ([d913f91](https://github.com/JeordyR/PyEventManager/commit/d913f91f8c24c0221832e4fda52da7a0d3f9fffe))


### Bug Fixes

* updated initial setup to support multiprocessing and spread out the code for easier extension ([a88a0f7](https://github.com/JeordyR/PyEventManager/commit/a88a0f7fb3ad4126a21b19860f20aaf0f08f3e20))
