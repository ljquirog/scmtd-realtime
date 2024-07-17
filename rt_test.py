from google.transit import gtfs_realtime_pb2
import requests
import datetime
import pandas as pd

feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://rt.scmetro.org/gtfsrt/trips')
feed.ParseFromString(response.content)

# Define the specific route_id and stop_id to search for
target_route_id = '19'
target_stop_id = '1551'

# Find current trip_id that corresponds to stop_id

# Read the GTFS stop_times.txt file
stop_times_df = pd.read_csv('stop_times.txt')

# Ensure the stop_id column is treated as a string
stop_times_df['stop_id'] = stop_times_df['stop_id'].astype(str)

# Filter the DataFrame for the given stop_id
filtered_df = stop_times_df.loc[stop_times_df['stop_id'] == target_stop_id].copy()

# Convert the arrival_time to datetime.time format
filtered_df.loc[:, 'arrival_time'] = pd.to_datetime(filtered_df['arrival_time'], format='%H:%M:%S').dt.time

# Get the current time
current_time = datetime.datetime.now().time()

# Function to get the time difference
def time_diff(t1, t2):
    t1_seconds = t1.hour * 3600 + t1.minute * 60 + t1.second
    t2_seconds = t2.hour * 3600 + t2.minute * 60 + t2.second
    return abs(t1_seconds - t2_seconds)

# Find the closest arrival time to the current time
closest_row = filtered_df.iloc[(filtered_df['arrival_time'].apply(lambda x: time_diff(x, current_time))).argsort()[:1]]
print(closest_row)

# Get the trip_id and arrival_time of the closest row
closest_trip_id = closest_row['trip_id'].values[0]
closest_arrival_time = closest_row['arrival_time'].values[0]

# Find & print what stop we're at 
stops_df = pd.read_csv('stops.txt')

stops_df['stop_id'] = stops_df['stop_id'].astype(str)

# Filter the DataFrame for the given stop_id
stop_name = stops_df.loc[stops_df['stop_id'] == target_stop_id, 'stop_name']

# Check if the stop_id was found and print the stop_name
if not stop_name.empty:
    print(f"Stop Name for stop_id {target_stop_id}: {stop_name.iloc[0]}")
else:
    print(f"No stop name found for stop_id {target_stop_id}")

# iterate through entries in the feed
for entity in feed.entity:
  if entity.HasField('trip_update'):
    trip_update = entity.trip_update
    # print(trip_update.trip.route_id)
    if trip_update.trip.route_id == target_route_id:
        for stop_time_update in trip_update.stop_time_update:
            # print(stop_time_update.stop_id)
            if stop_time_update.stop_id == target_stop_id:
                print(f"Route ID: {target_route_id}")
                print(f"Stop ID: {target_stop_id}")
                print(f"Trip ID: {trip_update.trip.trip_id}")            

                if stop_time_update.HasField('arrival'):
                    real_arrival_time = stop_time_update.arrival.time
                    
                    # Convert the Unix timestamp to a datetime object
                    arrival_datetime = datetime.datetime.fromtimestamp(real_arrival_time)
                    print(f"Realtime Arrival: {arrival_datetime.strftime('%H:%M:%S')}") # %Y-%m-%d 

                    print(f"Expected Arrival: {closest_arrival_time}")

                else:
                    print("No departure time available")



# now that i've automated it:
# - set up github
# - set up github actions
# - figure out how i want the data formatted for data collection -- aggregate to a csv file?
    # - look at kyle bcycle data
# - how to visualize aggregation

