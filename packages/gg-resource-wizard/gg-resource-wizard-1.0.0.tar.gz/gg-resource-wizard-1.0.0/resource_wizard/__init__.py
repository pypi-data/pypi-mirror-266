"""
Create resource modules for gg-core.
"""

from pathlib import Path

import click

__version__ = "1.0.0"


@click.group()
def rwiz():
    pass


@rwiz.command("create", help="Create a new resource module")
@click.argument(
    "output_dir",
    required=False,
    default="./src/features/",
    type=click.Path(dir_okay=True, path_type=Path, file_okay=False, exists=False),
)
def create_module(output_dir: Path):
    from cookiecutter.main import cookiecutter

    cookiecutter(
        str((Path(__file__).parent / "cookiecutter-resource").resolve()),
        output_dir=output_dir.resolve(),
    )
