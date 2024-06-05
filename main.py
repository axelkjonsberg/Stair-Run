"""
Main script to process OSM file to filter stairs and ski jumps
"""

import argparse
import logging
import os
from stairs_handler import StairsHandler
from filters import group_stairs, remove_duplicates, filter_by_step_count
from file_handling import validate_input_file, write_filtered_stairs_to_file, write_ski_jumps_to_file

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

parser = argparse.ArgumentParser(description='Process OSM file to filter stairs and ski jumps.')
parser.add_argument('input_file', type=str, help='Input OSM file (.osm, .o5m, .pbf)')
args = parser.parse_args()
input_file = args.input_file

validate_input_file(input_file)

handler = StairsHandler()
handler.apply_file(input_file, locations=True)

grouped_stairs = group_stairs(handler.stairs)
unique_stairs = remove_duplicates(grouped_stairs)
filtered_stairs = filter_by_step_count(unique_stairs)

# Create output directory
OUTPUT_DIR = ".output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

base_name = os.path.splitext(os.path.basename(input_file))[0]
for category, stairs in filtered_stairs.items():
    write_filtered_stairs_to_file(stairs, os.path.join(OUTPUT_DIR, f"{base_name}_stairs_{category}.osm"))

# Write ski jumps to a separate file
write_ski_jumps_to_file(handler.ski_jumps, os.path.join(OUTPUT_DIR, f"{base_name}_ski_jumps.osm"))
