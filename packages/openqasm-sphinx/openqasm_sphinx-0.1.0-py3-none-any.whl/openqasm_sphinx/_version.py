# SPDX-License-Identifier: Apache-2.0

import subprocess
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parent
REPO_ROOT = PACKAGE_ROOT.parents[1]


def get_version():
    with open(PACKAGE_ROOT / "VERSION.txt", "r", encoding="utf8") as fptr:
        version = fptr.read().strip()
    if (REPO_ROOT / ".git").is_dir():
        try:
            out = subprocess.run(
                ["git", "rev-parse", "--short=7", "HEAD"], check=True, capture_output=True
            )
        except (subprocess.CalledProcessError, OSError):
            pass
        else:
            git_sha = out.stdout.decode("utf8").strip()
            version += f".dev0+{git_sha}"
    return version
