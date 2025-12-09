import argparse
from pathlib import Path

from utils import gpx as gpx_utils
from config import M_TO_FT_MULTIPLIER, M_TO_MI_MULTIPLIER, M_TO_KM_MULTIPLIER

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a summary of a gpx file.",
    )
    parser.add_argument(
        "gpxFile",
        type=Path,
        help=".gpx file to summarize"
    )
    parser.add_argument(
        "--imperial",
        action="store_true",
        help="Print distances in miles/feet instead of km/m",
    )
    return parser.parse_args(argv)

if __name__ == "__main__":
    args = parse_args()

    df = gpx_utils.gpx_to_df(args.gpxFile)
    distance = df['cum_distance'].iloc[-1]
    elevation_gain = df['cum_altitude_gain'].iloc[-1]

    if args.imperial:
        distance *= M_TO_MI_MULTIPLIER
        elevation_gain *= M_TO_FT_MULTIPLIER
        print(f"Distance: {distance:.2f} miles")
        print(f"Elevation Gain: {elevation_gain:.2f} feet")
    else:
        distance *= M_TO_KM_MULTIPLIER
        print(f"Distance: {distance:.2f} km")
        print(f"Elevation Gain: {elevation_gain:.2f} meters")
