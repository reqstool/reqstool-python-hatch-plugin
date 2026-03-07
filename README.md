[![Commit Activity](https://img.shields.io/github/commit-activity/m/reqstool/reqstool-python-hatch-plugin?label=commits&style=for-the-badge)](https://github.com/reqstool/reqstool-python-hatch-plugin/pulse)
[![GitHub Issues](https://img.shields.io/github/issues/reqstool/reqstool-python-hatch-plugin?style=for-the-badge&logo=github)](https://github.com/reqstool/reqstool-python-hatch-plugin/issues)
[![License](https://img.shields.io/github/license/reqstool/reqstool-python-hatch-plugin?style=for-the-badge&logo=opensourceinitiative)](https://opensource.org/license/mit/)
[![Build](https://img.shields.io/github/actions/workflow/status/reqstool/reqstool-python-hatch-plugin/build.yml?style=for-the-badge&logo=github)](https://github.com/reqstool/reqstool-python-hatch-plugin/actions/workflows/build.yml)
[![Documentation](https://img.shields.io/badge/Documentation-blue?style=for-the-badge&link=docs)](https://reqstool.github.io)

# Reqstool Python Hatch Plugin

Hatch build hook plugin for [reqstool](https://github.com/reqstool/reqstool-client) that collects decorated code and generates `annotations.yml` during `hatch build`.

## Installation

Add to your `pyproject.toml`:

```toml
[build-system]
requires = [
  "hatchling",
  "reqstool-python-hatch-plugin==<version>",
]
```

## Usage

Configure the plugin in `pyproject.toml`:

```toml
[tool.hatch.build.hooks.reqstool]
sources = ["src", "tests"]
test_results = "build/**/junit.xml"
dataset_directory = "docs/reqstool"
output_directory = "build/reqstool"
```

The plugin uses [reqstool-python-decorators](https://github.com/reqstool/reqstool-python-decorators) for processing.

## Documentation

Full documentation can be found [here](https://reqstool.github.io).

## Contributing

See the organization-wide [CONTRIBUTING.md](https://github.com/reqstool/.github/blob/main/CONTRIBUTING.md).

## License

MIT License.
