# Labelsmith: An Open-Source Productivity Suite for Data Annotators

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Project Status: Beta – Initial beta release, core functionality implemented but lacking test coverage.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

## ⚠️ Beta Release Notice

**Important:** Labelsmith is currently in its beta stage (v0.0.1b3). While core functionality is implemented and the software is usable, please note:

- The project is still developing its comprehensive test suite.
- It may contain bugs and is subject to changes as we refine the project.
- The API may undergo modifications based on user feedback and further development.

We welcome early adopters and greatly appreciate your feedback. However, please exercise caution when implementing in production environments.

## Project Description

**Labelsmith** is an open-source Python project designed to streamline data annotators' workflows. Our goal is to create a robust, extensible toolkit that empowers data annotators to maximize their productivity, accuracy, and job satisfaction while contributing to the advancement of AI and machine learning projects.

Labelsmith is a project of LabelSTREAM (Label Syndicate for Transparency, Responsibility, and Ethicality in Algorithmic Management), an organization committed to improving the landscape of data annotation and algorithmic management.

### Current Features

The `labelsmith` package currently offers the following core modules:

1. **`shyft`**: A comprehensive shift-logging application built on the `tkinter` GUI framework. Key features include:
   
   - Automatic shift duration tracking with a configurable, always-on-top timer
   - Task metadata recording and note-taking interface
   - Local data persistence for shift entries and tasking history
   - Full CRUD operations for shift records
   - Autologger functionality for streamlined task logging

2. **`utils`**: A collection of utility scripts aimed at optimizing annotator workflows:
   - `utils.income`: Includes the `simulate` function for modeling earnings scenarios based on various workload parameters
   - `utils.metrics`: Provides productivity and earnings analysis tools

## Installation

```bash
pip install labelsmith
```

We recommend installing in a virtual environment for testing purposes.

## Contributing

We welcome contributions from developers of all skill levels! Check out our [CONTRIBUTING.md](https://github.com/labelstream/labelsmith/blob/main/CONTRIBUTING.md) for guidelines on how to get started.

## Roadmap

1. **[HIGH PRIORITY] Expand test coverage**
2. Enhance productivity visualization tools
3. Implement tabbed interface for task history review
4. Develop plugin system for custom annotator tools
5. Expand and improve core functionality of the `shyft` module
6. Create comprehensive documentation and API reference

## Recent Changes (v0.0.1b3)

- Fixed issue with shift log files not being properly persisted locally
- Corrected UI bug preventing theme changes
- Improved focus management in entry dialogs

For a full list of changes, please see our [CHANGELOG.md](https://github.com/labelstream/labelsmith/blob/main/CHANGELOG.md).

## License

Labelsmith is licensed under the Apache License, Version 2.0. See the [LICENSE](https://github.com/labelstream/labelsmith/blob/main/LICENSE) file for the full license text.

## Copyright and Attribution

Copyright 2024 LabelSTREAM Contributors.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

Labelsmith is under active development. Star [this repo](https://github.com/labelstream/labelsmith) to stay updated on our progress, and feel free to open issues for feature requests or bug reports. Together, we're working toward a future in which data annotators are more empowered and better equipped to make an even greater impact in the world of AI and machine learning. Join us! 🚀

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied. The authors and contributors of Labelsmith are not responsible for any damages or liabilities associated with its use.