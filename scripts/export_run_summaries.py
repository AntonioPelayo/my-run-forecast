import datetime
import pandas as pd

from utils.activity import activities_summary
from utils.config import DATA_PATH, PARQUET_RUN_ACTIVITIES_PATH

def main() -> None:
    summaries = activities_summary(PARQUET_RUN_ACTIVITIES_PATH)
    df = pd.DataFrame(summaries)

    filename = DATA_PATH / f"run_summaries.csv"
    df.to_csv(filename, index=False)
    print(f"Exported run activity summaries to {filename}")

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = DATA_PATH / f"backups/run_summaries_{timestamp}.csv"
    df.to_csv(backup_filename, index=False)
    print(f"Exported backup run activity summaries to {backup_filename}")


if __name__ == '__main__':
    main()
