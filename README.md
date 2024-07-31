# Labelsmith: An Open-Source Productivity Suite for Data Annotators

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)
[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip)

## ⚠️ Alpha Release Notice

**Important:** Labelsmith is currently in its early alpha stage (v0.0.1a6). It is not yet ready for production use. Features may be incomplete, and significant changes may occur between versions. Use at your own risk.

## Project Description

**Labelsmith** is an open-source Python project designed to streamline data annotators' workflows. Our goal is to create a robust, extensible toolkit that empowers the data science and machine learning community.

### Current Features

The `labelsmith` package currently offers the following core modules:

1. **`shyft`**: A comprehensive shift-logging application built on the `tkinter` GUI framework. Key features include:
   
   - Automatic shift duration tracking with a configurable, always-on-top timer
   - Task metadata recording and note-taking interface
   - Local data persistence for shift entries and tasking history
   - Full CRUD operations for shift records

2. **`utils`**: A collection of utility scripts aimed at optimizing annotator workflows:
   - `utils.income`: Includes the `simulate` function for modeling earnings scenarios based on various workload parameters

## Installation

```bash
pip install labelsmith
```

Please note that this is an alpha release and may not be stable. It is recommended to install in a virtual environment for testing purposes.

## Contributing

We welcome contributions from developers of all skill levels! Check out our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to get started.

## Roadmap

- [x] Implement `utils.metrics` module
- [ ] Add unit tests and increase code coverage
- [ ] Develop plugin system for custom annotator tools
- [ ] Create comprehensive documentation and API reference

## License

Labelsmith is licensed under the Apache License, Version 2.0. See the [LICENSE](LICENSE) file for the full license text.

## Copyright and Attribution

Copyright 2024 Labelsmith Contributors.

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

Labelsmith is under active development. Star this repo to stay updated on our progress, and feel free to open issues for feature requests or bug reports. Together, we're working toward a future in which data annotators find themselves more empowered and better equipped to make an even greater impact in the world of AI and machine learning. Join us! 🚀

## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied. The authors and contributors of Labelsmith are not responsible for any damages or liabilities associated with its use.