import numpy as np
from typing import Tuple

from utils.map_primitives import Polyline
from utils.typing import NDArrayFloat

class PedestrianCrossing:
    id: int
    edge1: Polyline
    edge2: Polyline

    @classmethod
    def build(cls):
        pass

    def get_edges_2d(self) -> Tuple[NDArrayFloat, NDArrayFloat]:
        """Retrieve the two principal edges of the crosswalk, in 2d.

        Returns:
            edge1: array of shape (2,2), a 2d polyline representing one edge of the crosswalk, with 2 waypoints.
            edge2: array of shape (2,2), a 2d polyline representing the other edge of the crosswalk, with 2 waypoints.
        """
        return (self.edge1.xyz[:, :2], self.edge2.xyz[:, :2])

    def __eq__(self, other: object) -> bool:
        """Check if two pedestrian crossing objects are equal, up to a tolerance."""
        if not isinstance(other, PedestrianCrossing):
            return False

        return np.allclose(self.edge1.xyz, other.edge1.xyz) and np.allclose(self.edge2.xyz, other.edge2.xyz)

    @property
    def polygon(self) -> NDArrayFloat:
        """Return the vertices of the polygon representing the pedestrian crossing.

        Returns:
            array of shape (N,3) representing vertices. The first and last vertex that are provided are identical.
        """
        v0, v1 = self.edge1.xyz
        v2, v3 = self.edge2.xyz
        return np.array([v0, v1, v3, v2, v0])