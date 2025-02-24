# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

### Changed

### Removed


## [0.1.4] - 2025-02-22

### Changed

- Move coffer definitions in coffers module
- Finish rsync plugin
- Fix WRITE mode vs APPEND mode : don't extract files in WRITE mode


## [0.1.2] - 2025-02-22

### Changed

- Fix mtime saving
- Fix instance/class metchods in Config


## [0.1.1] - 2025-02-20

### Changed

- Fix bug in lock


## [0.1.0] - 2025-02-20

### Added

- AES cryptography

### Changed

- !!! Compatibility broken !!! Switch from Fernet to Aes for better
  performance for bank coffer


## [0.0.10] - 2025-02-19

### Added

- Test for file locking
- Benchmark
- Add new coffer types : bank, store, market and null
- Add plugin extensions
- Add plugin for password with import from chrome
- Add plugin for encrypting/decrypting external files using coffer key

### Changed

- Finished CLI
- Split store to support other containers class
- Fix recursive import or directories
- Fix reading files in a writable coffer
- Update locking strategy
- Fix tmp cleaning


## [0.0.9] - 2025-02-09

### Added

- Add FernetStore and open method

### Changed

- Fix fileobj propagation


## [0.0.8] - 2025-02-07

### Added

- Test for lzma
- Failing test for gzip : io.UnsupportedOperation: Negative seek in write mode not supported
- Failing tests for tar append ... normal
- Add fast and furious zstd FernetFile class and open function

### Changed

- Change raised exceptions to io.* ones


## [0.0.7] - 2025-02-05

### Added

- Test for encrypting existing file
- Add documentation

### Removed

- Remove unused mtime parameter


## [0.0.6] - 2025-02-05

### Changed

- Update classifiers


## [0.0.5] - 2025-02-05

### Changed

- Fix tests
- Update doc

### Removed

- Support for python 3.8
- Support for python 3.13 (codecov-cli not compatible)


## [0.0.4] - 2025-02-04

### Changed

- Fix packaging


## [0.0.3] - 2025-02-04

### Changed

- Update doc
- Update test


## [0.0.2] - 2025-02-02

### Added

- Initial release
