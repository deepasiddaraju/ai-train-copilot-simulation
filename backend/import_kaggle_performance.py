import pandas as pd
import sqlite3
import os

DB_FILE = "railways.db"
DATA_FOLDER = "data"

def import_kaggle_performance():
    conn = sqlite3.connect(DB_FILE)

    kaggle_file = os.path.join(DATA_FOLDER, "kaggle_train_performance.csv")
    if not os.path.exists(kaggle_file):
        print("❌ Kaggle performance file not found in data folder.")
        return

    df = pd.read_csv(kaggle_file)
    print("📊 Columns loaded:", df.columns.tolist())

    # Rename Kaggle columns to match schema
    df = df.rename(columns={
        "train_number": "train_no",
        "average_delay_minutes": "avg_delay_minutes",
        "pct_right_time": "pct_on_time",
        "pct_slight_delay": "pct_slight_delay",
        "pct_significant_delay": "pct_significant_delay",
        "pct_cancelled_unknown": "pct_cancelled"
    })

    # Keep only needed columns
    df = df[["train_no","station_code","avg_delay_minutes","pct_on_time",
             "pct_slight_delay","pct_significant_delay","pct_cancelled",
             "scraped_at","source_url"]]

    # Write to SQLite
    df.to_sql("train_performance", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Kaggle train performance data imported successfully!")

if __name__ == "__main__":
    import_kaggle_performance()
