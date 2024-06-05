# Stair Run Finder

This tool processes OpenStreetMap data to identify and categorize stairs based on their step count.

Below is an example result from the tool: several stairs in Oslo categorized as different map layers.
![Map of Oslo with different stairs found by the ](Images/image.png)
(Maps like this can be created by uploading .osm data to [umap](https://umap.openstreetmap.fr/en/map/new))

## Requirements

- Python 3.6+
- pip

## Installation

1. Clone the repository.
2. Install the required Python packages:

```sh
pip install -r requirements.txt
```

## Usage

Run the script with your OSM file as an argument:
```sh
python3 main.py <path to your .osm/.o5m/.pbf map>
```

This will produce an output folder in the same directory as main.py containing different maps for different lengths of stairs.

## Where to get OSM files

From one of the following sources:
* https://download.bbbike.org/osm/bbbike/
* https://www.openstreetmap.org/
* https://planet.openstreetmap.org/
* https://download.geofabrik.de/
