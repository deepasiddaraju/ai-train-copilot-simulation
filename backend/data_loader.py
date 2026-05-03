import pandas as pd
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

def load_stations(path=os.path.join(DATA_DIR, "stations.json")):
    with open(path, "r", encoding="utf-8") as f:
        stations_data = json.load(f)
    stations = pd.json_normalize(stations_data['features'])
    stations_df = stations[['properties.code','properties.name','properties.zone',
                            'properties.state','geometry.coordinates']].copy()
    stations_df.columns = ['code','name','zone','state','coordinates']
    stations_df['lon'] = stations_df['coordinates'].apply(lambda x: x[0] if isinstance(x, list) else None)
    stations_df['lat'] = stations_df['coordinates'].apply(lambda x: x[1] if isinstance(x, list) else None)
    return stations_df

def load_trains(path=os.path.join(DATA_DIR, "trains.json")):
    with open(path, "r", encoding="utf-8") as f:
        trains_data = json.load(f)
    trains = pd.json_normalize(trains_data['features'])
    # Based on GeoJSON schema: train number and name are inside properties
    trains_df = trains[['properties.number','properties.name']].copy()
    trains_df.columns = ['train_number','train_name']
    return trains_df

def load_schedules(path=os.path.join(DATA_DIR, "schedules.json")):
    schedules = pd.read_json(path)
    schedules_df = schedules[['train_number','train_name','station_code',
                              'station_name','arrival','departure']].copy()
    return schedules_df
