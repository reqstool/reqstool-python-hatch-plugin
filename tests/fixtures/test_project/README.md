# mypackage

Minimal test project for manual validation of `reqstool-python-hatch-plugin`.

## Prerequisites

A `.venv` must exist inside this directory with the plugin, Hatch, pytest, and reqstool installed.
If it is missing, recreate it from `tests/fixtures/test_project/`:

```bash
python3.13 -m venv .venv
.venv/bin/pip install -e ../../../   # install plugin in editable mode
.venv/bin/pip install hatch pytest reqstool
```

## Validation

Run all commands from `tests/fixtures/test_project/`.

### 1 — Run tests

```bash
.venv/bin/pytest tests/ --junit-xml=build/test-results/junit.xml -v
```

Expected: `test_hello` passes.

### 2 — Build

```bash
HATCH_ENV_TYPE_VIRTUAL_PATH=.venv .venv/bin/hatch build
```

Expected output (sdist phase):
1. `[reqstool] plugin <x.y.z> loaded`
2. `[reqstool] added reqstool_config.yml to dist/mypackage-0.1.0.tar.gz`

### 3 — Check artefacts

```bash
# annotations.yml must exist locally
test -f build/reqstool/annotations.yml && echo "OK: annotations.yml"

# reqstool_config.yml must NOT be in project root (injected directly into tarball)
test ! -f reqstool_config.yml && echo "OK: no loose reqstool_config.yml"

# sdist must contain reqstool_config.yml and dataset files
tar -tzf dist/mypackage-0.1.0.tar.gz | sort
```

Expected entries in the sdist:
- `mypackage-0.1.0/reqstool_config.yml`
- `mypackage-0.1.0/docs/reqstool/requirements.yml`
- `mypackage-0.1.0/docs/reqstool/software_verification_cases.yml`

Note: unlike the poetry plugin, hatch injects `reqstool_config.yml` directly into the tarball
and does not bundle `annotations.yml` — those are generated locally in `build/reqstool/`.

### 4 — Run reqstool status

Extract the sdist and merge in the local build outputs, then run `reqstool status`:

```bash
mkdir -p /tmp/mypackage-reqstool
tar -xzf dist/mypackage-0.1.0.tar.gz -C /tmp/mypackage-reqstool
mkdir -p /tmp/mypackage-reqstool/mypackage-0.1.0/build/reqstool
mkdir -p /tmp/mypackage-reqstool/mypackage-0.1.0/build/test-results
cp build/reqstool/annotations.yml /tmp/mypackage-reqstool/mypackage-0.1.0/build/reqstool/
cp build/test-results/junit.xml    /tmp/mypackage-reqstool/mypackage-0.1.0/build/test-results/
.venv/bin/reqstool status local -p /tmp/mypackage-reqstool/mypackage-0.1.0
```

Expected: all green — `REQ_001` implemented, `T1 P1`, no missing tests or SVCs.
