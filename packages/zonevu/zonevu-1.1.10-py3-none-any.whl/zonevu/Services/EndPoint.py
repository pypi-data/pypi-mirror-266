from dataclasses import  dataclass
from dataclasses_json import dataclass_json, DataClassJsonMixin
import argparse
from .Error import ZonevuError
import os
from pathlib import Path
from typing import ClassVar, Union, Dict


# @dataclass_json
@dataclass
class EndPoint(DataClassJsonMixin):
    apikey: str
    verify: bool = False
    base_url: str = 'zonevu.ubiterra.com'
    std_keyfile_name: ClassVar[str] = 'zonevu_keyfile.json'

    @classmethod
    def from_key(cls, apiKey: str) -> 'EndPoint':
        return cls(apiKey)

    @classmethod
    def from_keyfile(cls) -> 'EndPoint':
        """
        Creates an EndPoint instance from a json file whose path is provided in the command line.
        User either -k or --keyfile to pass in as an argument the path to the key json file.
        Here is an example key json file:
        {
            "apikey": "xxxx-xxxxx-xxxxx-xxxx"
        }
        @return: An Endpoint instance
        """
        parser = argparse.ArgumentParser()
        parser.add_argument("-k", "--keyfile", type=str)  # Path/Filename to key file
        args, unknown = parser.parse_known_args()
        key_path = args.keyfile
        if key_path is None:
            raise ZonevuError.local('the parameter --keyfile must be specified in the command line')

        return cls.from_keyfile_path(key_path)

    @classmethod
    def from_json_dict(cls, json_dict: Dict) -> 'EndPoint':
        return EndPoint.from_dict(json_dict)

    @classmethod
    def from_keyfile_path(cls, key_path: Union[str, Path]) -> 'EndPoint':
        if not os.path.exists(key_path):
            raise ZonevuError.local('keyfile "%s" not found' % key_path)

        with open(key_path, 'r') as file:
            args_json = file.read()
            instance = cls.from_json(args_json)
            return instance

    @classmethod
    def from_std_keyfile(cls) -> 'EndPoint':
        """
        Creates an EndPoint instance from a json file named 'zonevuconfig.json, stored in the OS user directory.'
        Here is an example key json file:
        {
            "apikey": "xxxx-xxxxx-xxxxx-xxxx"
        }
        @return: An Endpoint instance
        """
        std_keyfile_path = Path(Path.home(), cls.std_keyfile_name)
        return cls.from_keyfile_path(std_keyfile_path)
