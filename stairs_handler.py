"""
Handler for processing stairs and ski jumps from OSM data.
"""

import logging
import osmium
import shapely.geometry as geom
from shapely.geometry import LineString

LOG_INTERVAL = 1000

class StairsHandler(osmium.SimpleHandler):
    """
    Handler class for processing stairs and ski jumps from OSM data.
    """
    def __init__(self):
        osmium.SimpleHandler.__init__(self)
        self.stairs = []
        self.ski_jumps = []
        self.node_count = 0
        self.way_count = 0

    def add_stair(self, location, step_count):
        """
        Add a stair to the list if the location is valid.
        """
        if not location.valid():
            logging.warning("Invalid location: %s", location)
            return

        point = geom.Point(location.lon, location.lat)
        self.stairs.append((point, step_count))
        logging.debug('Added stair: %s, step_count: %d', point, step_count)

    def add_ski_jump(self, location):
        """
        Add a ski jump to the list.
        """
        point = geom.Point(location.lon, location.lat)
        self.ski_jumps.append(point)
        logging.debug('Added ski jump: %s', point)

    def add_long_stair(self, way):
        """
        Add a long stair to the list.
        """
        points = [(n.location.lon, n.location.lat) for n in way.nodes if n.location.valid()]
        line = LineString(points)
        for point in line.coords:
            self.stairs.append((geom.Point(point), 0))
        logging.debug('Added long stair: %s', line)

    def node(self, n):
        """
        Add a node as a stair or ski jump.
        """
        self.node_count += 1
        if self.node_count % LOG_INTERVAL == 0:
            logging.info("Processing node %d", self.node_count)

        if self.is_valid_stair(n):
            self.add_stair(n.location, int(n.tags["step_count"]))
            return

        if self.is_valid_ski_jump(n):
            self.add_ski_jump(n.location)

    def way(self, w):
        """
        Add a way as a stair or ski jump.
        """
        self.way_count += 1
        if self.way_count % LOG_INTERVAL == 0:
            logging.info("Processing way %d", self.way_count)

        if self.is_valid_stair(w):
            self.process_stair_way(w)
            return

        if self.is_valid_ski_jump(w):
            self.process_ski_jump_way(w)

    def process_stair_way(self, way):
        """
        Process a way element representing stairs.
        """
        step_count = int(way.tags["step_count"])
        has_valid_node = False

        for n_idx, n in enumerate(way.nodes):
            if n_idx % LOG_INTERVAL == 0:
                logging.info("Processing node %d in way %d", n_idx, way.id)
            location = n.location
            logging.debug("Raw node data: id=%d, location=(%f,%f), valid=%s",
                n.ref, location.lat_without_check(), location.lon_without_check(), location.valid())

            if location.valid():
                has_valid_node = True
                self.add_stair(location, step_count)
            else:
                logging.warning("Invalid location for node %d in way %d", n.ref, way.id)

        if not has_valid_node:
            logging.warning("No valid nodes found in way %d", way.id)
        elif self.is_long_stair(way):
            self.add_long_stair(way)

    def process_ski_jump_way(self, way):
        """
        Process a way element representing a ski jump.
        """
        points = [(n.location.lon, n.location.lat) for _, n in enumerate(way.nodes) if n.location.valid()]
        if len(points) < 2:
            logging.warning("No valid nodes for ski jump in way %d", way.id)
            return
        line = LineString(points)
        self.ski_jumps.append(line)
        logging.debug('Added ski jump way: %s', line)

    @staticmethod
    def is_valid_stair(element):
        """
        Check if an element is a valid stair.
        """
        return "highway" in element.tags and element.tags["highway"] == "steps" and "step_count" in element.tags and int(element.tags["step_count"]) > 25

    @staticmethod
    def is_valid_ski_jump(element):
        """
        Check if an element is a valid ski jump.
        """
        return ("piste:type" in element.tags and element.tags["piste:type"] == "ski_jump") or ("man_made" in element.tags and element.tags["man_made"] == "ski_jump")

    @staticmethod
    def is_long_stair(way):
        """
        Check if a way element represents a long stair.
        """
        if "highway" not in way.tags or way.tags["highway"] != "steps":
            return False

        points = [(n.location.lon, n.location.lat) for n in way.nodes if n.location.valid()]
        if len(points) < 2:
            return False

        line = LineString(points)
        return line.length > 50
    