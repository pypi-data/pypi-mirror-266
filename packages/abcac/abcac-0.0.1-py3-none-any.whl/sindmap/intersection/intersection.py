import numpy as np
from dataclasses import dataclass
from enum import Enum, unique
from typing import List, Optional, Dict, Tuple

from map.stretch.stretch import Stretch
from map.lane.lane_segment import Lane, LaneType
from map.utils.map_primitives import Polyline, Point, LaneAdj, LaneSegmentAdj


@unique
class IntersectionType(str, Enum):
    """Describes the sorts of objects that may use the lane for travel."""

    LeftTurn: str = "LeftTurn"
    RightTurn: str = "RightTurn"
    Straight: str = "Straight"
    Inflow: str = "Inflow"
    Outflow: str = "Outflow"


@dataclass
class Intersection:
    id: int  # 2 digits
    type: List[IntersectionType]
    index: int
    predecessors: List[int]
    successors: List[int]
    vector_lanes: List[Lane]

    @classmethod
    def build(cls, intersection_data: dict) -> 'Intersection, Dict[int, Stretch]':
        Lane.set_shared_param(intersection_data['split_distance'], intersection_data['segment_point_num'])
        vector_lanes, vector_stretches_new = cls.get_vector_lanes(intersection_data)


        intersection_data.update({'vector_lanes': vector_lanes})
        return cls(id=intersection_data['id'],
                   type=intersection_data['type'],
                   index=intersection_data['index'],
                   predecessors=intersection_data['predecessors'],
                   successors=intersection_data['successors'],
                   vector_lanes=intersection_data['vector_lanes'],
                   ), vector_stretches_new

    @classmethod
    def get_vector_lanes(cls, intersection_data: dict) -> Dict[int, Lane]:
        vector_stretches = intersection_data['vector_stretches']
        Lane.set_shared_param(intersection_data['split_distance'], intersection_data['segment_point_num'])
        vector_lanes = {}
        lane_id = 1
        for pre_id in intersection_data['predecessors']:
            predecessor = vector_stretches[pre_id]
            for suc_id in intersection_data['successors']:
                successor = vector_stretches[suc_id]
                sub_vector_lanes, predecessor_new, successor_new = cls.get_sub_vector_lanes(predecessor, successor,
                                                            IntersectionType[intersection_data['type']],
                                                            lane_id)

                vector_stretches[pre_id] = predecessor_new
                vector_stretches[suc_id] = successor_new
                vector_lanes.update(sub_vector_lanes)
                lane_id += len(sub_vector_lanes)

        return vector_lanes, vector_stretches


    @classmethod
    def get_sub_vector_lanes(cls, predecessor: Stretch, successor: Stretch,
                             intersection_type: IntersectionType,
                             lane_id: int) -> Dict[int, Lane]:
        sub_vector_lanes = {}
        for pre_id, lane_pre in predecessor.vector_lanes.items():
            for suc_id, lane_suc in successor.vector_lanes.items():
                # intersection->lane->start == predecessor->lane->end
                start_point = lane_pre.get_end_point()
                # intersection->lane->end == successor->lane->start
                end_point = lane_suc.get_start_point()

                right_lane_boundary, left_lane_boundary = cls.generate_lane_boundaries(start_point, end_point, intersection_type)
                lane_data = {
                    'id': lane_id,
                    'lane_type': LaneType.determine_new_type(lane_pre.lane_type, lane_suc.lane_type),
                    'right_lane_boundary': right_lane_boundary,
                    'left_lane_boundary': left_lane_boundary,
                    'right_neighbor_id': None,
                    'left_neighbor_id': None
                }
                lane = Lane.build(lane_data)

                section_id = list(set(predecessor.successors) & set(successor.predecessors))
                assert len(section_id) == 1
                attr_data = {
                    'section_id': section_id[0],
                    'is_intersection': True
                }
                lane.add_attributes(attr_data)

                cls.get_links(lane_pre, lane_suc, lane)

                sub_vector_lanes[lane.id] = lane
                lane_id += 1

        return sub_vector_lanes, predecessor, successor

    @classmethod
    def get_links(cls, lane_pre: Lane, lane_suc: Lane, lane: Lane) -> None:
        """
        add predecessors/successors between lanes(intersection & stretch) and lane_segments
        """
        # lane level
        lane.predecessors = [LaneAdj(lane_pre.section_id, lane_pre.id)]
        lane.successors = [LaneAdj(lane_suc.section_id, lane_suc.id)]

        lane_pre.successors.append(LaneAdj(lane.section_id, lane.id))
        lane_suc.predecessors.append(LaneAdj(lane.section_id, lane.id))

        # lane_segment level
        start_lane_seg = lane.get_start_segment()
        end_lane_seg = lane.get_end_segment()
        end_lane_pre_seg = lane_pre.get_end_segment()
        start_lane_suc_seg = lane_suc.get_start_segment()

        start_lane_seg.predecessors.append(LaneSegmentAdj(end_lane_pre_seg.section_id,
                                                          end_lane_pre_seg.lane_id, end_lane_pre_seg.id))
        end_lane_seg.successors.append(LaneSegmentAdj(start_lane_suc_seg.section_id,
                                                      start_lane_suc_seg.lane_id, start_lane_suc_seg.id))

        end_lane_pre_seg.successors.append(LaneSegmentAdj(start_lane_seg.section_id,
                                                          start_lane_seg.lane_id, start_lane_seg.id))
        start_lane_suc_seg.predecessors.append(LaneSegmentAdj(end_lane_seg.section_id,
                                                              end_lane_seg.lane_id, end_lane_seg.id))



    @classmethod
    def generate_lane_boundaries(cls, start_point: Tuple[Point, Point], end_point: Tuple[Point, Point],
                                 lane_type: IntersectionType) -> Tuple[Polyline, Polyline]:
        """Generate left and right boundaries for a lane."""
        if lane_type == IntersectionType.Straight:
            total_distance = start_point[0].distance_to(end_point[0])
            if total_distance <= Lane.split_distance:
                num_points = 0
            else:
                num_points =  int(total_distance // Lane.split_distance) - 1

            right_boundary = cls.generate_line_points(start_point[0], end_point[0], num_points)
            left_boundary = cls.generate_line_points(start_point[1], end_point[1], num_points)
        else:
            # TODO: distance * 2.22 -> chord to 1/4 arc
            total_distance = start_point[0].distance_to(end_point[0]) * 2.22
            if total_distance <= Lane.split_distance:
                num_points = 0
            else:
                num_points = int(total_distance // Lane.split_distance) - 1

            # Extend the lines to find the intersection point (center of the arc)
            extended_start_point = (Point(start_point[0].x - (start_point[1].x - start_point[0].x),
                                          start_point[0].y - (start_point[1].y - start_point[0].y)),
                                    Point(start_point[1].x + (start_point[1].x - start_point[0].x),
                                          start_point[1].y + (start_point[1].y - start_point[0].y)))
            extended_end_point = (Point(end_point[0].x - (end_point[1].x - end_point[0].x),
                                        end_point[0].y - (end_point[1].y - end_point[0].y)),
                                  Point(end_point[1].x + (end_point[1].x - end_point[0].x),
                                        end_point[1].y + (end_point[1].y - end_point[0].y)))
            center = cls.line_intersection(extended_start_point, extended_end_point)
            if center is None:
                raise ValueError("Cannot determine the center of the arc. The lines might be parallel or coincident.")
            clockwise = (lane_type == IntersectionType.RightTurn)
            right_boundary = cls.generate_arc_points(center, start_point[0], end_point[0],
                                                     num_points, clockwise=clockwise)
            left_boundary = cls.generate_arc_points(center, start_point[1], end_point[1],
                                                    num_points, clockwise=clockwise)
        return Polyline(left_boundary), Polyline(right_boundary)

    @classmethod
    def generate_line_points(cls, start: Point, end: Point, num_points: int) -> List[Point]:
        """Generate points on a straight line between start and end."""
        return [Point(start.x + i * (end.x - start.x) / (num_points - 1),
                      start.y + i * (end.y - start.y) / (num_points - 1))
                for i in range(num_points)]

    @classmethod
    def generate_arc_points(cls, center: Point, start: Point, end: Point, num_points,
                                                            clockwise: bool = True) -> List[Point]:
        """Generate points on an arc with a given center, start, and end points."""
        radius = ((start.x - center.x) ** 2 + (start.y - center.y) ** 2) ** 0.5
        angle_start = np.arctan2(start.y - center.y, start.x - center.x)
        angle_end = np.arctan2(end.y - center.y, end.x - center.x)
        if clockwise:
            if angle_start < angle_end:
                angle_start += 2 * np.pi
        else:
            if angle_start > angle_end:
                angle_end += 2 * np.pi
        return [Point(center.x + radius * np.cos(angle_start + i * (angle_end - angle_start) / (num_points - 1)),
                      center.y + radius * np.sin(angle_start + i * (angle_end - angle_start) / (num_points - 1)))
                for i in range(num_points)]

    @classmethod
    def line_intersection(cls, line1: Tuple[Point, Point], line2: Tuple[Point, Point]) -> Point:
        """Calculate the intersection point of two lines."""
        x1, y1 = line1[0].x, line1[0].y
        x2, y2 = line1[1].x, line1[1].y
        x3, y3 = line2[0].x, line2[0].y
        x4, y4 = line2[1].x, line2[1].y
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if denom == 0:
            return None  # Lines are parallel or coincident
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / denom
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / denom
        return Point(px, py)


