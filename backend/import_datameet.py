import pandas as pd
import sqlite3
import os
import json

DB_FILE = "railways.db"
DATA_FOLDER = "data"

def import_datameet():
    conn = sqlite3.connect(DB_FILE)

    # --- Stations (GeoJSON flatten) ---
    with open(os.path.join(DATA_FOLDER, "stations.json"), "r", encoding="utf-8") as f:
        stations_data = json.load(f)

    features = stations_data["features"]
    stations = pd.json_normalize(features)

    stations["station_code"] = stations["properties.code"]
    stations["station_name"] = stations["properties.name"]
    stations["zone"] = stations["properties.zone"]
    stations["lon"] = stations["geometry.coordinates"].apply(lambda x: x[0] if isinstance(x, list) else None)
    stations["lat"] = stations["geometry.coordinates"].apply(lambda x: x[1] if isinstance(x, list) else None)

    stations = stations[["station_code", "station_name", "zone", "lat", "lon"]]

    # --- Merge zone mapping for major junctions ---
    zone_map_file = os.path.join(DATA_FOLDER, "station_zones.csv")
    if os.path.exists(zone_map_file):
        zone_map = pd.read_csv(zone_map_file)
        stations = stations.merge(zone_map, on="station_code", how="left", suffixes=("", "_mapped"))
        stations["zone"] = stations["zone"].fillna(stations["zone_mapped"])
        stations = stations.drop(columns=["zone_mapped"])

    stations.to_sql("stations", conn, if_exists="replace", index=False)

    # --- Trains ---
    with open(os.path.join(DATA_FOLDER, "trains.json"), "r", encoding="utf-8") as f:
        trains_data = json.load(f)

    features = trains_data["features"]
    trains = pd.json_normalize(features)

    trains["train_no"] = trains["properties.number"]
    trains["train_name"] = trains["properties.name"]
    trains["train_type"] = trains["properties.type"]

    trains = trains[["train_no", "train_name", "train_type"]]
    trains.to_sql("trains", conn, if_exists="replace", index=False)

    # --- Schedules ---
    schedules = pd.read_json(os.path.join(DATA_FOLDER, "schedules.json"))
    schedules = schedules.rename(columns={"train_number": "train_no"})
    schedules.to_sql("schedules", conn, if_exists="replace", index=False)

    conn.close()
    print("✅ Datameet Railways dataset imported successfully into SQLite!")

if __name__ == "__main__":
    import_datameet()
