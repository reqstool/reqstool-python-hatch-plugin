#!/usr/bin/env python3
# Copyright © LFV
"""Self-apply reqstool-python-decorators' processor to this repo's own src/tests,
producing build/reqstool/annotations.yml for `reqstool status` to consume."""

from reqstool_python_decorators.processors.decorator_processor import DecoratorProcessor

if __name__ == "__main__":
    DecoratorProcessor().process_decorated_data(
        # tests/fixtures holds a self-contained fixture project with its own decorated
        # REQ_001/SVC_001, unrelated to this plugin's own requirements -- excluded so it
        # doesn't pollute this repo's own traceability data.
        # tests/integration is omitted entirely: it's currently just empty __init__.py
        # stubs, add it back once real integration tests land there.
        path_to_python_files=["src", "tests/unit", "tests/e2e"],
        output_file="build/reqstool/annotations.yml",
    )
