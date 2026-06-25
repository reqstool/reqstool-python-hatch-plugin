# Copyright © LFV
import shutil
import subprocess
import tarfile
import tempfile
import venv
from pathlib import Path

import pytest
from reqstool_python_decorators.decorators.decorators import SVCs

FIXTURE_DIR = Path(__file__).parents[2] / "fixtures" / "test_project"
DIST_DIR = Path(__file__).parents[3] / "dist"

# The hatch plugin appends reqstool_config.yml to the tar.gz and generates
# annotations.yml on disk. requirements.yml, software_verification_cases.yml, and
# manual_verification_results.yml are all included via the sdist include config
# (docs/reqstool/**). The hook does NOT bundle the actual test-result XML files into
# the tarball -- it only records the configured glob pattern as a reqstool_config.yml
# resource (test results are transient CI artifacts, not shipped in the package).
EXPECTED_IN_TARBALL = [
    "reqstool_config.yml",
    "requirements.yml",
    "software_verification_cases.yml",
    "manual_verification_results.yml",
]


def _build_fixture_sdist(tmpdir: str) -> tuple[Path, Path]:
    """Builds the fixture project's sdist via an isolated venv with the local plugin
    wheel pre-installed (bypassing hatch's own build-env management, which can't
    resolve `@ file://` hook dependencies reliably across pip/uv versions).

    Returns (tarball_path, project_dir).
    """
    tmp_project = Path(tmpdir) / "test_project"
    # Keep build/test-results/junit.xml (the committed test_results fixture the hook
    # bundles into the sdist) but drop dist/__pycache__. ignore_patterns matches by
    # basename anywhere in the tree, so "build/reqstool" can't be excluded this way
    # without also matching docs/reqstool -- removed separately below instead.
    shutil.copytree(FIXTURE_DIR, tmp_project, ignore=shutil.ignore_patterns("dist", "__pycache__"))
    shutil.rmtree(tmp_project / "build" / "reqstool", ignore_errors=True)

    venv_dir = Path(tmpdir) / "build-venv"
    venv.create(str(venv_dir), with_pip=True)
    python = str(venv_dir / "bin" / "python")

    wheels = sorted(DIST_DIR.glob("reqstool_python_hatch_plugin-*.whl"))
    if not wheels:
        pytest.skip("No local wheel found — run `hatch build --target wheel` first")

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

    return tarballs[-1], tmp_project


@pytest.mark.e2e
@SVCs("SVC_HATCH_PLUGIN_001")
def test_hatch_build_generates_annotations_yml():
    """hatch build's `initialize` hook generates annotations.yml from decorated source,
    independently of whether the sdist-bundling (`finalize`) hook also succeeds."""
    with tempfile.TemporaryDirectory() as tmpdir:
        _, tmp_project = _build_fixture_sdist(tmpdir)

        annotations_file = tmp_project / "build" / "reqstool" / "annotations.yml"
        assert annotations_file.exists(), f"annotations.yml not generated at {annotations_file}"
        annotations_content = annotations_file.read_text()
        assert "REQ_001" in annotations_content, "annotations.yml missing REQ_001"
        assert "SVC_001" in annotations_content, "annotations.yml missing SVC_001"


@pytest.mark.e2e
@SVCs("SVC_HATCH_PLUGIN_002")
def test_hatch_build_sdist_bundles_reqstool_dataset():
    """hatch build's `finalize` hook bundles the full reqstool dataset -- including the
    optional manual_verification_results.yml and configured test_results glob -- into
    the sdist tarball, independently of whether annotation generation also succeeds."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tarball, _ = _build_fixture_sdist(tmpdir)

        with tarfile.open(tarball) as tf:
            names = tf.getnames()
            for expected in EXPECTED_IN_TARBALL:
                assert any(expected in n for n in names), f"{expected!r} missing from {tarball.name};\ngot: {names}"

            config_member = next(n for n in names if n.endswith("reqstool_config.yml"))
            config_fileobj = tf.extractfile(config_member)
            assert config_fileobj is not None, f"{config_member!r} is not a regular file"
            config_content = config_fileobj.read().decode()
            assert "test_results" in config_content, "reqstool_config.yml missing test_results"
            assert "junit.xml" in config_content, "reqstool_config.yml missing the configured test_results glob"
