# Changelog

All notable changes to Labelsmith will be documented in this file.

Labelsmith is an open-source productivity suite for data annotators, developed by LabelSTREAM ("Label Syndicate for Transparency, Responsibility, and Ethicality in Algorithmic Management"). It aims to streamline workflows and enhance productivity for professionals in the data annotation field.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Enhanced productivity visualization leveraging `labelsmith.utils.metrics`, offering more comprehensive ways to analyze and display productivity data
- Tabbed interface for the "Rank and Justification" window, enabling users to review their tasking history for the current shift while it's ongoing

### Changed
- Refactored "Manual Entry" and "Edit Shift" dialogs to return focus to the first item in the main GUI's tree view of shift records upon closing, enhancing user experience and navigation

### Fixed
- Focus management in "Manual Entry" and "Edit Shift" dialogs, ensuring proper return to the main view's shift record tree

### Planned
- Integration with external time tracking APIs for more comprehensive productivity analysis
- Dark mode option for reduced eye strain during night shifts

## [0.0.1b3] - 2024-08-01

### Fixed
- Resolved an issue where shift log files were not being properly locally persisted, ensuring data integrity across sessions
- Corrected a UI bug where the theme menu was always disabled, now allowing users to change application themes as intended

### Changed
- Transferred project to LabelSTREAM organization
- Updated project documentation to reflect the organizational change
- Implemented a custom dialog for the "Delete" functionality, improving user interaction and confirmation process

## [0.0.1b2] - 2024-08-01

### Added
- Implemented the ability to change the tax rate in the Totals window, providing more accurate income calculations for different tax situations

### Changed
- Initial release under the LabelSTREAM organization
- Updated README and documentation to reflect new organizational structure

## [0.0.1b1] - 2024-07-31

### Changed
- Performed a complete refactor of the `labelsmith.shyft` module, significantly improving its structure and maintainability
- Modularized the `shyft` codebase from a single script into three core modules: `core`, `gui`, and `utils`
- Each core module within `shyft` now contains multiple submodules for better organization and separation of concerns

### Added
- Improved error handling and logging throughout the `shyft` module
- Enhanced documentation for each new submodule

## [0.0.1a4] - 2024-07-25
## [0.0.1a3] - 2024-07-25
## [0.0.1a2] - 2024-07-25
## [0.0.1a1] - 2024-07-24

- Alpha releases under previous management. These versions represented early development stages with rapid iterations. Specific changes were not documented in detail.

## [0.0.1] - 2024-07-24

### Added
- Initial release of Labelsmith
- Basic functionality for tracking work shifts
- Simple GUI for data entry and visualization
- Local data persistence using JSON storage

## License

Labelsmith is released under the Apache License, Version 2.0. See the LICENSE file in the project repository for full details.

[Unreleased]: https://github.com/LabelSTREAM/labelsmith/compare/v0.0.1b3...HEAD
[0.0.1b3]: https://github.com/LabelSTREAM/labelsmith/compare/v0.0.1b2...v0.0.1b3
[0.0.1b2]: https://github.com/LabelSTREAM/labelsmith/releases/tag/v0.0.1b2