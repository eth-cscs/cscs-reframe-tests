# Contributing Guide

Thank you for your interest in contributing to the `cscs-reframe-tests` repository!!

## Getting Started

1. Fork the repository on GitHub.
1. Clone your fork locally:
    ```bash
    git clone https://github.com/your-username/cscs-reframe-tests.git
    cd cscs-reframe-tests
    ```
1. Set the upstream remote:
    ```bash
    git remote add upstream https://github.com/eth-cscs/cscs-reframe-tests.git
    ```

## How to Contribute

- Report bugs by opening an issue. For CSCS members, Jira issues are better and probably will be scheduled faster.
- Propose new tests or improvements by creating a pull request.

## Different testing suites

The repository has tests for different pipelines. We are using tags to differentiate between the different cases:
- `production`: Generally short tests (<= 10 minutes and <= 8 nodes) that are expected to run daily in the gitlab runners.
- `maintenance`: Tests that will validate the system after an intervention.
- `vs-node-validator`: Single node tests that are expected to run with the local scheduler whenever a new node is booted. Ideally these tests are very short (< 1 minute).
<!-- - `benchmark`: ? -->

## Code Style Guidelines

- Maintain consistency with the current codebase.
- Follow [PEP8](https://www.python.org/dev/peps/pep-0008/) for Python code.

## Testing Your Changes

- Validate that your test runs successfully using ReFrame, using the `config/cscs.py` configuration file.
- For new tests it's important to add the context for the test in the description or with a few comments in the test class.
<!-- Add link to how to test, especially UENVs -->
<!-- - Pipilines for test? -->

## Submitting a Pull Request

1.  Create a test branch
    ```bash
    git checkout -b my-test
    ```

1. Commit your changes
    ```bash
    git commit -am "Add new test for XYZ"
    ```

1. Push your branch
    ```bash
    git push origin my-test
    ```

1. Open a PR against the `main` branch of the upstream repository and describe your changes.


## Contact

Need help? Open an issue or contact the maintainers on GitHub.

---

We appreciate your contributions and effort in helping make this project better!

