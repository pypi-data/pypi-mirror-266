from typing import List

from utils.map_primitives import Point

class DrivableArea:
    id: int
    area_boundary: List[Point]

    @classmethod
    def build(cls):
        pass