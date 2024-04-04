import argparse
import re
import os
from pathlib import Path
from typing import Union, Optional


class Input:
    @staticmethod
    def get_name_from_args(title: str = '') -> str:
        # Get a name from argument list or ask user for it
        parser = argparse.ArgumentParser()
        parser.add_argument("-n", "--name", type=str)  # Input well
        args, unknown = parser.parse_known_args()
        name = args.name

        # Not found in argument list so ask user
        if name is None:
            name = input("Enter %s name: " % title)  # Get name from user in console

        return name


class Naming:
    @staticmethod
    def slugify(name: str) -> str:
        title = name.lower()
        # Replace any non-alphanumeric character with a hyphen
        title = re.sub(r'\W+', '-', title)
        # Remove any leading or trailing hyphens
        slug = title.strip('-')
        # Assign the result to a variable named slug
        return slug

    @staticmethod
    def replace_forbidden_symbols(filename: str) -> str:
        forbidden = '\\/:*?"<>|'
        return ''.join([symbol for symbol in filename if symbol not in forbidden])

    @staticmethod
    def make_safe_name(name: str, identifier: Optional[Union[str, int]] = None) -> str:
        name_safe = Naming.replace_forbidden_symbols(name)
        name_safe = Naming.slugify(name_safe)
        if identifier is not None:
            name_safe = '%s-%s' % (name_safe, identifier)
        return name_safe

    @staticmethod
    def make_safe_name_default(name: Union[str, None], default: str, identifier: Optional[Union[str, int]] = None) -> str:
        name = name if name is not None and len(name) > 0 else default
        name_safe = Naming.replace_forbidden_symbols(name)
        name_safe = Naming.slugify(name_safe)
        if identifier is not None:
            name_safe = '%s-%s' % (name_safe, identifier)
        return name_safe

    @staticmethod
    def build_safe_entity_dir(parent_dir: Union[Path, str], entity_name: str,
                              identifier: Optional[Union[str, int]] = None) -> Path:
        entity_name_safe = Naming.make_safe_name(entity_name, identifier)
        path = Path(parent_dir, entity_name_safe)
        Naming.check_dir(path)
        return path

    @staticmethod
    def check_dir(dir_path: Path):
        if not dir_path.is_dir():
            dir_path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def create_dir_under_home(dir_name: str) -> Path:
        # Join the home directory with the given directory name
        new_dir = Path.home() / dir_name
        Naming.check_dir(new_dir)
        return new_dir


