from data_loader import load_stations, load_trains, load_schedules

def preprocess(df):
    stations = load_stations()
    trains = load_trains()
    schedules = load_schedules()

    # Build maps
    station_map = dict(zip(stations['code'], stations['name']))
    zone_map = dict(zip(stations['code'], stations['zone']))
    lat_map = dict(zip(stations['code'], stations['lat']))
    lon_map = dict(zip(stations['code'], stations['lon']))

    # Apply mappings
    df['SOURCE_STATION_NAME'] = df['SOURCE_STATION'].map(station_map).fillna(df['SOURCE_STATION'])
    df['DESTINATION_STATION_NAME'] = df['DESTINATION_STATION'].map(station_map).fillna(df['DESTINATION_STATION'])
    df['TRAIN_OPERATOR'] = df['SOURCE_STATION'].map(zone_map).fillna("Unknown Zone")
    df['SOURCE_LAT'] = df['SOURCE_STATION'].map(lat_map)
    df['SOURCE_LON'] = df['SOURCE_STATION'].map(lon_map)
    df['DEST_LAT'] = df['DESTINATION_STATION'].map(lat_map)
    df['DEST_LON'] = df['DESTINATION_STATION'].map(lon_map)

    # Merge train names
    df = df.merge(trains, on='train_number', how='left')

    # Merge schedule info
    df = df.merge(schedules[['train_number','station_code','arrival','departure']], 
                  on='train_number', how='left')

    return df
