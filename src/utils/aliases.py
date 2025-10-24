import shlex
import subprocess
from typing import Optional


def run_command(command: str, check: bool = False) -> None:
    """Run a shell command given as a single string, splitting safely."""
    print(f"Running: {command}")
    subprocess.run(shlex.split(command), check=check)


def precommit() -> None:
    """Run pre-commit hooks on all files."""
    run_command("uv run pre-commit run --all-files")


def typecheck(extra_args: Optional[str] = None) -> None:
    """Run static type checking with mypy."""
    cmd: str = "uv run mypy"
    if extra_args:
        cmd += f" {extra_args}"
    run_command(cmd)


def audit() -> None:
    """Run a security audit with pip-audit."""
    run_command("uv run pip-audit .")
