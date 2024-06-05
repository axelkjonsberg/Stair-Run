"""
Utility functions for file validation and writing OSM data to files.
"""

import os
import shapely.geometry as geom
from shapely.geometry import LineString

def validate_input_file(file_name):
    """
    Validate the input file format.
    """
    valid_extensions = ['.osm', '.o5m', '.pbf']
    file_extension = os.path.splitext(file_name)[1]
    if file_extension not in valid_extensions:
        raise ValueError(f"Invalid file format: {file_extension}. Supported formats are: {', '.join(valid_extensions)}")

def write_filtered_stairs_to_file(filtered_stairs, output_file):
    """
    Write filtered stairs to an OSM file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<osm version="0.6" generator="Python osmium">\n')
        for i, (point, step_count) in enumerate(filtered_stairs):
            f.write(f'  <node id="-{i+1}" lat="{point.y}" lon="{point.x}">\n')
            f.write('    <tag k="highway" v="steps"/>\n')
            f.write(f'    <tag k="step_count" v="{step_count}"/>\n')
            f.write('  </node>\n')
        f.write('</osm>\n')

def write_ski_jumps_to_file(ski_jumps, output_file):
    """
    Write ski jumps to an OSM file.
    """
    with open(output_file, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<osm version="0.6" generator="Python osmium">\n')
        for i, jump in enumerate(ski_jumps):
            if isinstance(jump, geom.Point):
                f.write(f'  <node id="-{i+1}" lat="{jump.y}" lon="{jump.x}">\n')
                f.write('    <tag k="man_made" v="ski_jump"/>\n')
                f.write('  </node>\n')
            elif isinstance(jump, LineString):
                f.write(f'  <way id="-{i+1}">\n')
                for j, _ in enumerate(jump.coords):
                    f.write(f'    <nd ref="-{i+1 * 1000 + j}"/>\n')
                f.write('    <tag k="man_made" v="ski_jump"/>\n')
                f.write('  </way>\n')
        f.write('</osm>\n')
