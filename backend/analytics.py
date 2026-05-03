import pandas as pd

def busiest_stations(df, top_n=10):
    """
    Find the busiest stations by counting arrivals + departures.
    """
    station_counts = df['station_code'].value_counts().reset_index()
    station_counts.columns = ['station_code', 'count']
    return station_counts.head(top_n)

def zone_density(df):
    """
    Count number of trains per zone/operator.
    """
    zone_counts = df['TRAIN_OPERATOR'].value_counts().reset_index()
    zone_counts.columns = ['zone', 'train_count']
    return zone_counts

def average_dwell_times(df):
    """
    Calculate average dwell time (departure - arrival) per station.
    """
    # Convert times to datetime
    # df['arrival_dt'] = pd.to_datetime(df['arrival'], errors='coerce')
    df['arrival_dt'] = pd.to_datetime(df['arrival'], format="%H:%M:%S", errors='coerce')
    df['departure_dt'] = pd.to_datetime(df['departure'], format="%H:%M:%S", errors='coerce')
    #df['departure_dt'] = pd.to_datetime(df['departure'], errors='coerce')

    df['dwell_minutes'] = (df['departure_dt'] - df['arrival_dt']).dt.total_seconds() / 60
    dwell_avg = df.groupby('station_code')['dwell_minutes'].mean().reset_index()
    dwell_avg.columns = ['station_code', 'avg_dwell_minutes']
    return dwell_avg.sort_values(by='avg_dwell_minutes', ascending=False)
