import os
import pathlib
from typing import Union, NoReturn
from zipfile import ZipFile, ZIP_DEFLATED

PathLike = Union[str, pathlib.Path]


def check_or_make_dir(p: PathLike):
    """Check if the directory exists, if not, create it."""
    p = pathlib.Path(p)
    if p.exists() and p.is_file():
        raise FileExistsError(f"{p} is a file, not a directory.")
    if not p.exists():
        p.mkdir(parents=True)


def zip_dir(path: str, zip_path: str) -> NoReturn:
    """
    Zip the contents of the directory at 'path' into a zip file located at 'zip_path'.

    Parameters:
    - path (str): The directory path to zip.
    - zip_path (str): The destination path for the created zip file.
    """
    with ZipFile(zip_path, 'w', ZIP_DEFLATED) as ziph:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                # Here we use os.path.relpath to calculate the relative file path
                # relative to the directory being zipped. This ensures that the zip
                # file maintains the directory structure.
                rel_path = os.path.relpath(file_path, start=path)
                ziph.write(file_path, rel_path)


__all__ = [
    "zip_dir",
    "PathLike",
    "check_or_make_dir",
]

