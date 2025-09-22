import argparse
from pathlib import Path

from utils import activity as au


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Print a summary of an activity.",
    )
    parser.add_argument("activityFile", type=Path, help="Activity .parquet file to summarize")
    return parser.parse_args(argv)

if __name__ == "__main__":
    args = parse_args()
    au.print_activity_summary(args.activityFile)