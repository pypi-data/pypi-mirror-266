# Changelog

All notable changes to the "SheetFusion" project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.5] - 2023-12-11

### Updated

- Updated `README.md` to reduce redundancy and improve clarity.

### Improved

- Change output file name from `exam_XXXX.pdf` to `XXXX.pdf` where `XXXX` is the exam number.

## [1.0.4] - 2023-12-08

### Changed

- Changed examples in `README.md` to use `python3 -m sheetfusion` instead of `sheetfusion`.

## [1.0.3] - 2023-12-08

### Fixed

- Fixed missing dependency (rich) in pyproject.toml.
- Fixed contact email in pyproject.toml.

## [1.0.2] - 2023-12-08

### Fixed

- Fixed error in version number in pyproject.toml.

## [1.0.1] - 2023-12-08

### Fixed

- Changed logo in `README.md` to be a link to the project's GitHub page.

## [1.0.0] - 2023-12-08

### Added

- Initial release of SheetFusion.
- Command-line interface for merging cover sheets with exams.
- Required arguments for specifying cover sheet and exam PDF files.
- Optional arguments for output directory and file overwrite functionality.
