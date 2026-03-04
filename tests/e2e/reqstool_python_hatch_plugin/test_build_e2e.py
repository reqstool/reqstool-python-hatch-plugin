# Copyright © LFV
import shutil
import subprocess
import sys
import tarfile
import tempfile
import venv
from pathlib import Path

import pytest

FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "test_project"
DIST_DIR = Path(__file__).parents[3] / "dist"

# The hatch plugin appends reqstool_config.yml to the tar.gz and generates
# annotations.yml on disk. requirements.yml and software_verification_cases.yml
# are included via the sdist include config (docs/reqstool/**).
EXPECTED_IN_TARBALL = [
    "reqstool_config.yml",
    "requirements.yml",
    "software_verification_cases.yml",
]


@pytest.mark.e2e
def test_hatch_build_sdist_contains_reqstool_artifacts():
    """hatch build (sdist) triggers the reqstool hook and bundles all artifacts.

    Runs hatchling directly inside an isolated venv that has the local plugin wheel
    pre-installed, bypassing hatch's own build-env management (which can't resolve
    @ file:// hook dependencies reliably across pip/uv versions).
    """
    wheels = sorted(DIST_DIR.glob("reqstool_python_hatch_plugin-*.whl"))
    if not wheels:
        pytest.skip("No local wheel found — run `hatch build --target wheel` first")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_project = Path(tmpdir) / "test_project"
        shutil.copytree(FIXTURE_DIR, tmp_project, ignore=shutil.ignore_patterns("dist", "build", "__pycache__"))

        # Build an isolated venv with hatchling + the local plugin wheel.
        # We call hatchling directly so we fully control what's installed.
        venv_dir = Path(tmpdir) / "build-venv"
        venv.create(str(venv_dir), with_pip=True)
        python = str(venv_dir / "bin" / "python")

        subprocess.run(
            [python, "-m", "pip", "install", "--quiet", "hatchling", str(wheels[-1])],
            check=True,
        )

        result = subprocess.run(
            [python, "-m", "hatchling", "build", "--target", "sdist"],
            cwd=tmp_project,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"hatchling build failed:\n{result.stderr}"

        tarballs = sorted((tmp_project / "dist").glob("mypackage-*.tar.gz"))
        assert tarballs, "No tarball found in dist/"

        with tarfile.open(tarballs[-1]) as tf:
            names = tf.getnames()

        for expected in EXPECTED_IN_TARBALL:
            assert any(expected in n for n in names), f"{expected!r} missing from {tarballs[-1].name};\ngot: {names}"

        # annotations.yml is generated on disk (not bundled in the tarball)
        annotations_file = tmp_project / "build" / "reqstool" / "annotations.yml"
        assert annotations_file.exists(), f"annotations.yml not generated at {annotations_file}"
        annotations_content = annotations_file.read_text()
        assert "REQ_001" in annotations_content, "annotations.yml missing REQ_001"
        assert "SVC_001" in annotations_content, "annotations.yml missing SVC_001"
