from dataclasses import dataclass
from typing import List, Optional, Dict

from map.lane.lane_segment import Lane, LaneSegment
from map.utils.map_primitives import Polyline

@dataclass
class Stretch:
    id: int     # 2 digits
    predecessors: List[int]
    successors: List[int]
    vector_lanes: Dict[int, Lane]
    opposite_stretch_id: Optional[int] = None


    @classmethod
    def build(cls, stretch_data: dict) -> 'Stretch':
        Lane.set_shared_param(stretch_data['split_distance'], stretch_data['segment_point_num'])

        vector_lanes = cls.get_vector_lanes(stretch_data)
        stretch_data.update({'vector_lanes': vector_lanes})
        return cls(id=stretch_data['id'],
                   predecessors=stretch_data['predecessors'],
                   successors=stretch_data['successors'],
                   vector_lanes=stretch_data['vector_lanes'],
                   opposite_stretch_id=stretch_data['opposite_stretch_id']
        )


    @classmethod
    def get_vector_lanes(cls, stretch_data: dict) -> Dict[int, Lane]:
        vector_lanes = {}
        for lane_data in stretch_data.get('lanes'):
            lane = Lane.build(lane_data)

            attr_data = {
                'section_id': stretch_data['id'],
                'is_intersection': False
            }
            lane.add_attributes(attr_data)

            vector_lanes[lane.id] = lane

        return vector_lanes