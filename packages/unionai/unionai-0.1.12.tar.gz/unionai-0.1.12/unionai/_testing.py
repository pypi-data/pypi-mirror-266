"""This module contains utils that are useful for development.

Example usage:

```python
import pandas as pd
from flytekit import task, workflow

from unionai._testing import imagespec_with_local_unionai

image = imagespec_with_local_unionai(packages=["pandas"])


@task(container_image=image)
def get_data() -> pd.DataFrame:
    return pd.DataFrame([1, 2, 3])


@task(container_image=image)
def double_df(df: pd.DataFrame) -> pd.DataFrame:
    return 2 * df


@workflow
def main() -> pd.DataFrame:
    df = get_data()
    return double_df(df=df)
```
"""

import os
import sys
from pathlib import Path
from shutil import rmtree
from subprocess import run
from typing import Optional

from flytekit import ImageSpec
from flytekit.core.context_manager import FlyteContextManager

import unionai


def imagespec_with_local_unionai(
    *args, packages: Optional[list] = None, source_root: Optional[str] = None, **kwargs
) -> Optional[ImageSpec]:
    """Creates an imagespec with local changes."""
    state = FlyteContextManager.current_context().execution_state
    if not (state and state.mode is None):
        return None

    unionai_root_path = Path(unionai.__path__[0]).parent

    assert (unionai_root_path / "pyproject.toml").exists(), "pyproject.toml needs to exists in root directory"

    if source_root is None:
        tmp_path = Path("tmp")
        source_root = tmp_path / "source_root"
        if source_root.exists():
            rmtree(source_root)
        source_root.mkdir(parents=True)
    else:
        source_root = Path(source_root)

    vendor_path = source_root / ".vendor"

    run([sys.executable, "-m", "build", "--outdir", vendor_path, "--wheel"], check=True, cwd=unionai_root_path)
    wheels = list(vendor_path.iterdir())
    assert len(wheels) == 1, f"There should be only one wheel in {vendor_path}"
    name = wheels[0].name

    packages = packages or []
    packages.append(f".vendor/{name}")

    return ImageSpec(*args, packages=packages, source_root=os.fspath(source_root), **kwargs)
