# import sqlite3

# conn = sqlite3.connect("railways.db")
# cursor = conn.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
# print(cursor.fetchall())
# conn.close()
# import json
# import pandas as pd
# import os

# DATA_FOLDER = "data"

# with open(os.path.join(DATA_FOLDER, "trains.json"), "r", encoding="utf-8") as f:
#     trains_data = json.load(f)

# features = trains_data["features"]
# df = pd.json_normalize(features)
# print(df.columns.tolist())
# print(df.head())

# with open(os.path.join(DATA_FOLDER, "stations.json"), "r", encoding="utf-8") as f:
#     stations_data = json.load(f)

# features = stations_data["features"]
# df = pd.json_normalize(features)
# print(df.columns.tolist())
# print(df.head())

# with open(os.path.join(DATA_FOLDER, "schedules.json"), "r", encoding="utf-8") as f:
#     schedules_data = json.load(f)

# df = pd.DataFrame(schedules_data)
# print(df.columns.tolist())
# print(df.head())

# import sqlite3
# conn = sqlite3.connect("railways.db")
# cursor = conn.cursor()

# print("Stations sample:")
# cursor.execute("SELECT * FROM stations LIMIT 5")
# print(cursor.fetchall())

# print("Trains sample:")
# cursor.execute("SELECT * FROM trains LIMIT 5")
# print(cursor.fetchall())

# print("Schedules sample:")
# cursor.execute("SELECT * FROM schedules LIMIT 5")
# print(cursor.fetchall())

# conn.close()
# import pandas as pd
# import os

# DATA_FOLDER = "data"
# kaggle_file = os.path.join(DATA_FOLDER, "kaggle_train_performance.csv")

# # Load the Kaggle dataset
# df = pd.read_csv(kaggle_file)

# # Print column names
# print("📊 Column names:", df.columns.tolist())

# # Print datatypes
# print("\n📊 Data types:")
# print(df.dtypes)

# # Print first 5 rows
# print("\n📊 First 5 rows:")
# print(df.head())





#railways.db
# import sqlite3, pandas as pd

# DB_FILE = "railways.db"
# conn = sqlite3.connect(DB_FILE)

# sql = """
# SELECT s.train_no, s.train_name, s.station_code, st.station_name,
#        p.avg_delay_minutes, p.pct_on_time, p.pct_slight_delay,
#        p.pct_significant_delay, p.pct_cancelled
# FROM schedules s
# JOIN stations st ON s.station_code = st.station_code
# JOIN train_performance p ON s.train_no = p.train_no AND s.station_code = p.station_code
# LIMIT 10;
# """

# df = pd.read_sql_query(sql, conn)
# conn.close()

# print(df.head())

import sqlite3
conn = sqlite3.connect("railways.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

cursor.execute("PRAGMA table_info(train_performance);")
print(cursor.fetchall())

import sqlite3
conn = sqlite3.connect("railways.db")
cursor = conn.cursor()

cursor.execute("SELECT DISTINCT train_no FROM train_performance LIMIT 20;")
print(cursor.fetchall())



