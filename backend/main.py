import pandas as pd
from preprocess import preprocess
from analytics import busiest_stations, zone_density, average_dwell_times

# Example dataset
df = pd.DataFrame({
    "SOURCE_STATION": ["FM","TCR","PBR"],
    "DESTINATION_STATION": ["R","GMO","TCR"],
    "train_number": ["47154","56044","19269"]
})

df = preprocess(df)

print("=== Busiest Stations ===")
print(busiest_stations(df))

print("\n=== Zone Density ===")
print(zone_density(df))

print("\n=== Average Dwell Times ===")
print(average_dwell_times(df).head(10))
