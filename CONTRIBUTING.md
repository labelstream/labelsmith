# Contributing to Labelsmith

Hello! I'm [`@kosmolebryce`](https://github.com/kosmolebryce), Labelsmith's creator. Thank you for your interest in contributing to Labelsmith, a project of LabelSTREAM (Label Syndicate for Transparency, Responsibility, and Ethicality in Algorithmic Management). We're excited to have you join our community of contributors.

## Project Mission and Status

Labelsmith is an open-source Python project designed to streamline data annotators' workflows. Our goal is to create a robust, extensible toolkit that empowers data annotators to maximize their productivity, accuracy, and job satisfaction while contributing to the advancement of AI and machine learning projects.

As part of LabelSTREAM, Labelsmith is committed to promoting transparency, responsibility, and ethicality in algorithmic management within the data annotation field.

Currently, Labelsmith is in its early beta stage (v0.0.1b2). While the core functionality is implemented and the software is usable, we are in a crucial phase of development:

- We are actively working on implementing a comprehensive test suite (highest priority).
- The API may undergo changes as we refine the project.
- We are focusing on stability and bug fixes.

We appreciate your patience and understanding as we work towards a more stable release.

## How to Contribute

1. **Fork the repository**: Start by forking the [Labelsmith repository](https://github.com/labelstream/labelsmith) to your own GitHub account.

2. **Clone your fork**: Clone your fork to your local machine for development.

3. **Create a new branch**: Always create a new branch for your changes. This keeps your fork's main branch clean and makes it easier to submit pull requests.

4. **Make your changes**: Implement your feature, bug fix, or tests.

5. **Follow the code style**: We use Black for code formatting. Please ensure your code adheres to this style.

6. **Write tests**: This is currently our highest priority. Add unit tests for any new functionality and ensure all tests pass.

7. **Update documentation**: If your changes require it, update the relevant documentation, including docstrings and README.md if necessary.

8. **Commit your changes**: Use clear and descriptive commit messages.

9. **Push to your fork**: Push your changes to your GitHub fork.

10. **Submit a pull request**: Create a pull request from your fork to the main Labelsmith repository.

## Current Focus Areas

We are currently focusing on:

1. **Implementing a comprehensive test suite** (Highest Priority)
2. Expanding and improving the core functionality of the `shyft` module.
3. Enhancing the `utils.metrics` module with more advanced analytics.
4. Improving documentation, especially user guides and API references.
5. Optimizing performance and usability of the GUI components.

Contributions in these areas are particularly welcome, but we're open to all improvements that align with our project mission and LabelSTREAM's goals!

## Code Quality

We strive for high-quality code. Please ensure your code is clean, well-documented, and follows Python best practices. As we are in the process of implementing our testing suite, we strongly encourage contributors to write tests for any new functionality they introduce.

## Setting Up the Development Environment

1. Create a virtual environment: `python -m venv venv`
2. Activate the virtual environment:
   - On Windows: `venv\Scripts\activate`
   - On macOS and Linux: `source venv/bin/activate`
3. Install the development dependencies: `pip install -r requirements.txt`
4. Install Labelsmith in editable mode: `pip install -e .`

## Running Tests

We are in the process of implementing our test suite using pytest. Once implemented, you will be able to run the tests using the following command from the project root:

```
pytest
```

In the meantime, we encourage contributors to write tests for their contributions and submit them along with their pull requests.

## Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions with other contributors. Discrimination, harassment, and disruptive behavior are not tolerated.

## Questions or Suggestions?

If you have any questions or suggestions, feel free to open an issue on our [GitHub repository](https://github.com/labelstream/labelsmith/issues) or [reach out to me directly](mailto:k.lebryce@pm.me).

Thank you for contributing to Labelsmith! Your efforts help make this project better for everyone and contribute to empowering data annotators worldwide while promoting transparency, responsibility, and ethicality in algorithmic management.