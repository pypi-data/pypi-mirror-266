import os
import os.path
import subprocess
from textwrap import dedent

import pytest

MNT_DATASET_ROWS = dedent(
    """
    01375.png
    07510.png
    08433.png
    mnist-info.txt
    readme.md
    val-info.md
    train-info.md
    02201.png
    02297.png
    08967.png
    01837.png
    05385.png
    09416.png
    01805.png
    06366.png
    08394.png
    00422.png
    04813.png
    05508.png
    07576.png
    08747.png
    00266.png
    06810.png
    08537.png
    09396.png
    09846.png
    00271.png
    00577.png
    01608.png
    07194.png
    08051.png
    """
)

MNT_FILE_TREE = {
    "01375.png": 324,
    "07510.png": 308,
    "08433.png": 224,
    "mnist-info.txt": 0,
    "readme.md": 1193,
    "train": {
        "1": {
            "00266.png": 186,
            "06810.png": 175,
            "08537.png": 206,
            "09396.png": 168,
            "09846.png": 208,
        },
        "2": {
            "00422.png": 257,
            "04813.png": 266,
            "05508.png": 287,
            "07576.png": 297,
            "08747.png": 319,
        },
        "3": {
            "00271.png": 303,
            "00577.png": 293,
            "01608.png": 243,
            "07194.png": 300,
            "08051.png": 304,
        },
        "train-info.md": 18,
    },
    "val": {
        "1": {
            "01837.png": 182,
            "05385.png": 182,
            "09416.png": 162,
        },
        "2": {
            "02201.png": 283,
            "02297.png": 274,
            "08967.png": 333,
        },
        "3": {
            "01805.png": 345,
            "06366.png": 302,
            "08394.png": 329,
        },
        "val-info.md": 20,
    },
}

# Note that these commands are tested in order.
E2E_STEPS = (
    {
        "command": (
            "dvcx",
            "ls",
            "--aws-anon",
            "s3://ldb-public/remote/datasets/dogs-and-cats/",
        ),
        "expected": dedent(
            """
            dogs-and-cats.tar.gz
            dogs-and-cats.zip
            license
            """
        ),
        "listing": True,
    },
    {
        "command": (
            "dvcx",
            "du",
            "--aws-anon",
            "s3://ldb-public/remote/datasets/dogs-and-cats/",
        ),
        "expected": "   9.2M s3://ldb-public/remote/datasets/dogs-and-cats/\n",
    },
    {
        "command": (
            "dvcx",
            "find",
            "--iname",
            "*DOG*",
            "--aws-anon",
            "s3://ldb-public/remote/datasets/",
        ),
        "expected": dedent(
            """
            s3://ldb-public/remote/datasets/Stanford-dog-breeds/
            s3://ldb-public/remote/datasets/dogs-and-cats/
            s3://ldb-public/remote/datasets/dogs-and-cats/dogs-and-cats.tar.gz
            s3://ldb-public/remote/datasets/dogs-and-cats/dogs-and-cats.zip
            """
        ),
        "listing": True,
    },
    {
        "command": ("dvcx", "du", "--aws-anon", "s3://ldb-public/remote/datasets/"),
        "expected": "  43.3G s3://ldb-public/remote/datasets/\n",
    },
    {
        "command": (
            "dvcx",
            "cp",
            "-r",
            "--aws-anon",
            "s3://ldb-public/remote/datasets/mnist-tiny/",
            "mnt-cp",
        ),
        "expected": "",
        "downloading": True,
        "instantiating": True,
        "files": {
            "mnt-cp": MNT_FILE_TREE,
        },
    },
    {
        "command": (
            "dvcx",
            "clone",
            "-r",
            "--aws-anon",
            "s3://ldb-public/remote/datasets/mnist-tiny/",
            "mnt",
        ),
        "expected": "",
        "downloading": True,
        "instantiating": True,
        "files": {
            "mnt": MNT_FILE_TREE,
        },
    },
    {
        "command": ("dvcx", "ls-datasets"),
        "expected": "mnt (v1)\n",
    },
    {
        "command": ("dvcx", "ls-dataset-rows", "mnt", "--version", "1"),
        "expected": MNT_DATASET_ROWS,
        "sort_expected_lines": True,
    },
    {
        "command": ("dvcx", "ls-datasets"),
        "expected": "mnt (v1)\n",
    },
    {
        "command": ("dvcx", "ls-dataset-rows", "mnt", "--version", "1"),
        "expected": MNT_DATASET_ROWS,
        "sort_expected_lines": True,
    },
    {
        "command": ("dvcx", "edit-dataset", "mnt", "--new-name", "mnt-new"),
        "expected": "",
    },
    {
        "command": ("dvcx", "ls-datasets"),
        "expected": "mnt-new (v1)\n",
    },
    {
        "command": ("dvcx", "ls-dataset-rows", "mnt-new", "--version", "1"),
        "expected": MNT_DATASET_ROWS,
        "sort_expected_lines": True,
    },
    {
        "command": ("dvcx", "rm-dataset", "mnt-new", "--version", "1"),
        "expected": "",
    },
    {
        "command": ("dvcx", "ls-datasets"),
        "expected": "",
    },
)


def verify_files(files, base=""):
    """Recursively validate file and directory structure."""
    for name, value in files.items():
        full_name = os.path.join(base, name)
        if isinstance(value, dict):
            assert os.path.isdir(full_name)
            verify_files(value, full_name)
        else:
            assert os.path.isfile(full_name)
            assert os.path.getsize(full_name) == value


def run_step(step):
    """Run an end-to-end test step with a command and expected output."""
    result = subprocess.run(
        step["command"],
        shell=False,  # noqa: S603
        capture_output=True,
        check=True,
        encoding="utf-8",
    )
    if step.get("sort_expected_lines"):
        assert sorted(result.stdout.split("\n")) == sorted(
            step["expected"].lstrip("\n").split("\n")
        )
    else:
        assert result.stdout == step["expected"].lstrip("\n")
    if step.get("listing"):
        assert "Listing" in result.stderr
    else:
        assert "Listing" not in result.stderr
    if step.get("downloading"):
        assert "Downloading" in result.stderr
    else:
        assert "Downloading" not in result.stderr
    if step.get("instantiating"):
        assert "Instantiating" in result.stderr
    else:
        assert "Instantiating" not in result.stderr
    files = step.get("files")
    if files:
        verify_files(files)


@pytest.mark.e2e
def test_cli_e2e(tmp_dir):
    """End-to-end CLI Test"""
    for step in E2E_STEPS:
        run_step(step)
