import json
import yaml
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from drivable_area import DrivableArea
from pedestrian_crossing import PedestrianCrossing
from stretch.stretch import Stretch
from intersection.intersection import Intersection
from lane.lane_segment import Lane, LaneSegment


@dataclass
class SinDStaticMap:
    city_name: str
    vector_drivable_areas: Dict[int, DrivableArea]
    vector_pedestrian_crossings = Dict[int, PedestrianCrossing]
    vector_stretches: Dict[int, Stretch]
    vector_intersections: Dict[int, Intersection]
    vector_lane_segments: Dict[int, LaneSegment]
    split_distance: float = None
    segment_point_num: int = None

    @classmethod
    def from_cfg(cls):
        with open('cfg/map_config.yaml', 'r') as file:
            config = yaml.safe_load(file)

        cls.split_distance = config['split_distance']
        cls.segment_point_num = config['segment_point_num']

    @classmethod
    def from_json(cls, map_data_path: Path):
        with map_data_path.open('r') as file:
            map_data = json.load(file)
        return map_data

    @classmethod
    def build(cls, map_data_path: Path) -> 'SinDStaticMap':
        cls.from_cfg()
        map_data = cls.from_json(map_data_path)

        vector_stretches = cls.build_stretches(map_data['stretch'])
        vector_intersections, vector_stretches = cls.build_intersections(map_data['intersection'], vector_stretches)
        vector_drivable_areas = cls.build_drivable_areas()
        vector_pedestrian_crossings = cls.build_pedestrian_crossings()
        vector_lane_segments = cls.get_lane_segments(vector_stretches, vector_intersections)

        return cls(
            city_name=map_data_path.stem,
            vector_stretches=vector_stretches,
            vector_intersections=vector_intersections,
            vector_lane_segments=vector_lane_segments,
            vector_drivable_areas=vector_drivable_areas,
            vector_pedestrian_crossings=vector_pedestrian_crossings
        )

    @classmethod
    def build_drivable_areas(cls):
        return None

    @classmethod
    def build_stretches(cls, stretches_data: List[Dict]) -> Dict[int, Stretch]:
        vector_stretches = {}
        for _, data in enumerate(stretches_data):
            data.update({
                'split_distance': cls.split_distance,
                'segment_point_num': cls.segment_point_num
            })
            stretch = Stretch.build(data)
            vector_stretches[stretch.id] = stretch

        return vector_stretches

    @classmethod
    def build_intersections(cls, intersections_data: List[Dict],
                            vector_stretches: Dict[int, Stretch]) -> Dict[int, Intersection]:
        vector_intersections = {}
        for _, data in enumerate(intersections_data):
            data.update({
                'split_distance': cls.split_distance,
                'segment_point_num': cls.segment_point_num,
                'vector_stretches': vector_stretches
            })
            intersection, vector_stretches = Intersection.build(data)
            vector_intersections[intersection.id] = intersection

        return vector_intersections, vector_stretches

    @classmethod
    def build_pedestrian_crossings(cls):
        return None

    @classmethod
    def get_lane_segments(cls, vector_stretches, vector_intersections):
        lane_segments = {}
        for _, stretch in vector_stretches.items():
            for _, lane in stretch.vector_lanes.items():
                for _, segment in lane.vector_lane_segments.items():
                    lane_segments[segment.unique_id] = segment

        for _, intersection in vector_intersections.items():
            for _, lane in intersection.vector_lanes.items():
                for _, segment in lane.vector_lane_segments.items():
                    lane_segments[segment.unique_id] = segment

        return lane_segments

if __name__ == '__main__':
    map_file_path = Path(r'C:\CLY\THU\Code\SinD_osm_process\data\tianjin.json')
    sm = SinDStaticMap.build(map_file_path)
    pass

