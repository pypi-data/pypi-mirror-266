import numpy as np
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import List, Optional, Dict, Tuple

from map.utils.map_primitives import Point, Polyline, LaneAdj, LaneSegmentAdj

@unique
class LaneType(str, Enum):
    """Describes the sorts of objects that may use the lane for travel."""
    VEHICLE: str = "VEHICLE"
    BIKE: str = "BIKE"
    BUS: str = "BUS"
    PEDESTRIAN: str = "PEDESTRIAN"

    def __init__(self, _):
        # set priority of TYPE, VEHICLE is the first
        cls = self.__class__
        if not hasattr(cls, '_priority_counter'):
            cls._priority_counter = len(cls.__members__)
        self.priority = cls._priority_counter
        cls._priority_counter -= 1

    @classmethod
    def determine_new_type(cls, predecessor_type: 'LaneType', successor_type: 'LaneType') -> 'LaneType':
        """Determine the new lane type based on predecessor and successor types."""
        if predecessor_type == successor_type:
            return predecessor_type
        else:
            return max(predecessor_type, successor_type, key=lambda x: x.priority)

@unique
class LaneMarkType(str, Enum):
    """Color and pattern of a painted lane marking, located on either the left or ride side of a lane segment.

    The `NONE` type indicates that lane boundary is not marked by any paint; its extent should be implicitly inferred.
    """

    DASH_SOLID_YELLOW: str = "DASH_SOLID_YELLOW"
    DASH_SOLID_WHITE: str = "DASH_SOLID_WHITE"
    DASHED_WHITE: str = "DASHED_WHITE"
    DASHED_YELLOW: str = "DASHED_YELLOW"
    DOUBLE_SOLID_YELLOW: str = "DOUBLE_SOLID_YELLOW"
    DOUBLE_SOLID_WHITE: str = "DOUBLE_SOLID_WHITE"
    DOUBLE_DASH_YELLOW: str = "DOUBLE_DASH_YELLOW"
    DOUBLE_DASH_WHITE: str = "DOUBLE_DASH_WHITE"
    SOLID_YELLOW: str = "SOLID_YELLOW"
    SOLID_WHITE: str = "SOLID_WHITE"
    SOLID_DASH_WHITE: str = "SOLID_DASH_WHITE"
    SOLID_DASH_YELLOW: str = "SOLID_DASH_YELLOW"
    SOLID_BLUE: str = "SOLID_BLUE"
    NONE: str = "NONE"
    UNKNOWN: str = "UNKNOWN"



@dataclass
class LaneSegment:
    id: int
    lane_type: LaneType
    right_lane_segment_boundary: Polyline
    left_lane_segment_boundary: Polyline
    predecessors: List[str] = field(default_factory=list)
    successors: List[str] = field(default_factory=list)
    unique_id: Optional[str] = None
    section_id: Optional[int] = None
    lane_id: Optional[int] = None
    is_intersection: bool = None
    right_neighbor_id: Optional[int] = None
    left_neighbor_id: Optional[int] = None

    @classmethod
    def build(cls, data: dict) -> 'LaneSegment':
        return cls(**data)


    def add_attributes(self, attrs_data: dict) -> None:
        self.add_section_id(attrs_data["section_id"])
        self.add_lane_id(attrs_data["lane_id"])
        self.add_is_intersection(attrs_data["is_intersection"])
        self.get_unique_id()

    def add_section_id(self, section_id: int) -> None:
        self.section_id = section_id

    def add_lane_id(self, lane_id: int) -> None:
        self.lane_id = lane_id

    def add_is_intersection(self, is_intersection):
        self.is_intersection = is_intersection

    def get_unique_id(self) -> None:
        assert self.section_id < 100 and self.lane_id < 100 and self.id < 10000
        self.unique_id = f"{self.section_id:02d}" + f"{self.lane_id:02d}" + f"{self.id:04d}"


@dataclass
class Lane:
    id: int
    lane_type: LaneType
    right_lane_boundary: Polyline
    left_lane_boundary: Polyline
    vector_lane_segments: Dict[int, LaneSegment]
    section_id: Optional[int] = None
    is_intersection: Optional[bool] = None
    predecessors: List[int] = field(default_factory=list)
    successors: List[int] = field(default_factory=list)
    right_neighbor_id: Optional[int] = None
    left_neighbor_id: Optional[int] = None

    split_distance: float = None
    segment_point_num: float = None


    @classmethod
    def set_shared_param(cls, split_distance, segment_point_num):
        cls.split_distance = split_distance
        cls.segment_point_num = segment_point_num


    @classmethod
    def build(cls, lane_data) -> 'Lane':
        id = lane_data['id']
        lane_type = LaneType[lane_data['lane_type']]
        right_lane_boundary = cls.get_lane_boundary(lane_data['right_lane_boundary'])
        left_lane_boundary = cls.get_lane_boundary(lane_data['left_lane_boundary'],
                                                   len(right_lane_boundary))
        assert len(right_lane_boundary) == len(left_lane_boundary)

        lane_segments_data = {
            'lane_type': lane_type,
            'right_lane_boundary': right_lane_boundary,
            'left_lane_boundary': left_lane_boundary
        }
        vector_lane_segments = cls.get_lane_segments(lane_segments_data)

        return cls(id=id,
                   lane_type=lane_type,
                   right_lane_boundary=right_lane_boundary,
                   left_lane_boundary=left_lane_boundary,
                   vector_lane_segments=vector_lane_segments,
                   right_neighbor_id=lane_data['right_neighbor_id'],
                   left_neighbor_id=lane_data['left_neighbor_id']
        )


    @classmethod
    def get_lane_boundary(cls, lane_boundary, lane_point_num=False) -> Polyline:
        # TODO: 应该把 get_lane_boundary 拆分到section中直接输入给Lane
        if isinstance(lane_boundary, Polyline):
            return lane_boundary

        start = Point(x=lane_boundary[0][0], y=lane_boundary[0][1])
        end = Point(x=lane_boundary[1][0], y=lane_boundary[1][1])

        if lane_point_num:
            insert_point_num = lane_point_num - 2
            waypoints = [start]
            for i in range(1, insert_point_num + 1):
                # Calculate the ratio of the current point along the line
                ratio = i / (insert_point_num + 1)
                # Linearly interpolate the x and y coordinates
                x = start.x + (end.x - start.x) * ratio
                y = start.y + (end.y - start.y) * ratio
                # Create a new Point object and add it to the list
                waypoints.append(Point(x=x, y=y))
            waypoints.append(end)
            return Polyline(waypoints=waypoints)

        else:
            vec = np.array(end.xy) - np.array(start.xy)
            norm = np.linalg.norm(vec)
            num_points = int(norm / cls.split_distance)
            if num_points < 1:
                return [start, end]

            delta = vec / num_points
            waypoints = [Point(x=start.x + delta[0] * i, y=start.y + delta[1] * i)\
                                       for i in range(1, num_points)]
            return Polyline(waypoints=[start]+waypoints+[end])

    @classmethod
    def get_lane_segments(cls, data: dict) -> Dict[int, LaneSegment]:
        lane_segments = {}
        total_points = len(data['right_lane_boundary'])
        segment_count = (total_points + 1) // cls.segment_point_num

        for i in range(segment_count):
            start_index = i * cls.segment_point_num
            end_index = min((i + 1) * cls.segment_point_num, total_points)
            right_lane_segment_boundary = Polyline(data['right_lane_boundary'].waypoints[start_index:end_index])
            left_lane_segment_boundary = Polyline(data['left_lane_boundary'].waypoints[start_index:end_index])

            lane_segment_data = {
                'id': i+1,
                'lane_type': data['lane_type'],
                'right_lane_segment_boundary': right_lane_segment_boundary,
                'left_lane_segment_boundary': left_lane_segment_boundary
            }
            lane_segment = LaneSegment.build(lane_segment_data)

            lane_segments[i+1]=lane_segment

        lane_segments = {k: lane_segments[k] for k in sorted(lane_segments)}
        return lane_segments


    def add_attributes(self, attrs_data: dict) -> None:
        self.add_section_id(attrs_data['section_id'])
        self.add_is_intersection(attrs_data['is_intersection'])
        attrs_data.update({'lane_id': self.id})

        for key, value in self.vector_lane_segments.items():
            value.add_attributes(attrs_data)

        self.get_segment_inter_adj()


    def add_section_id(self, section_id: int) -> None:
        self.section_id = section_id

    def add_is_intersection(self, is_intersection):
        self.is_intersection = is_intersection


    def get_segment_inter_adj(self):
        self.get_segment_inter_link()
        self.get_segment_inter_nbr()

    def get_segment_inter_link(self):
        segments = self.vector_lane_segments
        sorted_keys = sorted(segments.keys())
        for i, key in enumerate(sorted_keys):
            if i > 0:
                segments[key].predecessors = [LaneSegmentAdj(section_id=self.section_id,
                                                             lane_id=self.id,
                                                             segment_id=sorted_keys[i - 1])]
            if i < len(sorted_keys) - 1:
                segments[key].successors = [LaneSegmentAdj(section_id=self.section_id,
                                                           lane_id=self.id,
                                                           segment_id=sorted_keys[i + 1])]

    def get_segment_inter_nbr(self):
        pass

    def get_start_segment(self):
        return list(self.vector_lane_segments.values())[0]

    def get_end_segment(self):
        return list(self.vector_lane_segments.values())[-1]

    def get_start_point(self) -> Tuple[Point, Point]:
        start_segment = self.get_start_segment()
        return (start_segment.right_lane_segment_boundary.waypoints[0],
                start_segment.left_lane_segment_boundary.waypoints[0])

    def get_end_point(self) -> Tuple[Point, Point]:
        end_segment = self.get_end_segment()
        return (end_segment.right_lane_segment_boundary.waypoints[-1],
                end_segment.left_lane_segment_boundary.waypoints[-1])
