import datetime
import pandas as pd

from utils.activity import activities_summary
from utils.config import DATA_PATH, PARQUET_RUN_ACTIVITIES_PATH

def main():
    summaries = activities_summary(PARQUET_RUN_ACTIVITIES_PATH)
    df = pd.DataFrame(summaries)
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = DATA_PATH / f"run_summaries_{timestamp}.csv"
    df.to_csv(filename, index=False)
    print(f"Exported run activity summaries to {filename}")


if __name__ == '__main__':
    main()