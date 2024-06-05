import osmium
import shapely.geometry as geom
from shapely.geometry import LineString
import logging

class StairsHandler(osmium.SimpleHandler):
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.stairs = []
        self.ski_jumps = []
        self.node_count = 0
        self.way_count = 0

    def add_stair(self, location, step_count):
        if not location.valid():
            logging.warning(f"Invalid location: {location}")
            return
        
        point = geom.Point(location.lon, location.lat)
        self.stairs.append((point, step_count))
        logging.debug(f'Added stair: {point}, step_count: {step_count}')

    def add_ski_jump(self, location):
        point = geom.Point(location.lon, location.lat)
        self.ski_jumps.append(point)
        logging.debug(f'Added ski jump: {point}')

    def add_long_stair(self, way):
        points = [(n.location.lon, n.location.lat) for n in way.nodes if n.location.valid()]
        line = LineString(points)
        for point in line.coords:
            self.stairs.append((geom.Point(point), 0))
        logging.debug(f'Added long stair: {line}')

    def node(self, n):
        self.node_count += 1
        if self.node_count % 1000 == 0:
            logging.info(f"Processing node {self.node_count}")

        if self.is_valid_stair(n):
            self.add_stair(n.location, int(n.tags["step_count"]))
            return
        
        if self.is_valid_ski_jump(n):
            self.add_ski_jump(n.location)

    def way(self, w):
        self.way_count += 1
        if self.way_count % 1000 == 0:
            logging.info(f"Processing way {self.way_count}")

        if self.is_valid_stair(w):
            self.process_stair_way(w)
            return
        
        if self.is_valid_ski_jump(w):
            self.process_ski_jump_way(w)

    def process_stair_way(self, way):
        step_count = int(way.tags["step_count"])
        has_valid_node = False

        for n_idx, n in enumerate(way.nodes):
            if n_idx % 1000 == 0:
                logging.info(f"Processing node {n_idx} in way {way.id}")
            location = n.location
            logging.debug(f"Raw node data: id={n.ref}, location=({location.lat_without_check()},{location.lon_without_check()}), valid={location.valid()}")

            if location.valid():
                has_valid_node = True
                self.add_stair(location, step_count)
            else:
                logging.warning(f"Invalid location for node {n.ref} in way {way.id}")

        if not has_valid_node:
            logging.warning(f"No valid nodes found in way {way.id}")
        elif self.is_long_stair(way):
            self.add_long_stair(way)

    def process_ski_jump_way(self, way):
        points = [(n.location.lon, n.location.lat) for n_idx, n in enumerate(way.nodes) if n.location.valid()]
        if len(points) < 2:
            logging.warning(f"No valid nodes for ski jump in way {way.id}")
            return
        line = LineString(points)
        self.ski_jumps.append(line)
        logging.debug(f'Added ski jump way: {line}')

    @staticmethod
    def is_valid_stair(element):
        return "highway" in element.tags and element.tags["highway"] == "steps" and "step_count" in element.tags and int(element.tags["step_count"]) > 25

    @staticmethod
    def is_valid_ski_jump(element):
        return ("piste:type" in element.tags and element.tags["piste:type"] == "ski_jump") or ("man_made" in element.tags and element.tags["man_made"] == "ski_jump")

    @staticmethod
    def is_long_stair(way):
        if "highway" not in way.tags or way.tags["highway"] != "steps":
            return False
        
        points = [(n.location.lon, n.location.lat) for n in way.nodes if n.location.valid()]
        if len(points) < 2:
            return False
        
        line = LineString(points)
        return line.length > 50
