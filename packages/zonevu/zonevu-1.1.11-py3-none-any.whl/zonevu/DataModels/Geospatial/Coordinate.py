from dataclasses import dataclass
from dataclasses_json import LetterCase, config, DataClassJsonMixin
import math


@dataclass
class Coordinate(DataClassJsonMixin):
    dataclass_json_config = config(letter_case=LetterCase.PASCAL)["dataclasses_json"]
    x: float = 0
    y: float = 0

    def rotate(self, angle: float) -> 'Coordinate':
        """
        Rotates this point around the origin by an angle
        @param angle: angle from x-axis in radians
        @return: the rotated point
        """
        x = self.x * math.cos(angle) - self.y * math.sin(angle)
        y = self.x * math.sin(angle) + self.y * math.cos(angle)
        return Coordinate(x, y)

    def __add__(self, other: 'Coordinate') -> 'Coordinate':
        return Coordinate(self.x + other.x, self.y + other.y)
