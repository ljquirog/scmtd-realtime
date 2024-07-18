# - figure out how i want the data formatted for data collection -- aggregate to a csv file?
    # - look at kyle bcycle data
# - set up github actions
# - update so it collects for multiple/all stops along one route (find way to automate)
# - rename each file per route
# - how to visualize aggregation

# daily aggregation of all csv files for all routes

from google.transit import gtfs_realtime_pb2
import requests
from datetime import datetime
import pandas as pd
import os


feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('https://rt.scmetro.org/gtfsrt/trips')
feed.ParseFromString(response.content)

# Function to get the time difference
def time_diff(t1, t2):
    t1_seconds = t1.hour * 3600 + t1.minute * 60 + t1.second
    t2_seconds = t2.hour * 3600 + t2.minute * 60 + t2.second
    return abs(t1_seconds - t2_seconds)

# Define the specific route_id and stop_id to search for... this varname could be clearer
def generate_realtime(target_route_id, target_stop_id):
    real_arrival_time = '99999'
    actual_trip_id = '99999'

    # Find current trip_id that corresponds to stop_id
    # Read the GTFS stop_times.txt file
    stop_times_df = pd.read_csv('gtfs-static/stop_times.txt')

    # Ensure the stop_id column is treated as a string
    stop_times_df['stop_id'] = stop_times_df['stop_id'].astype(str)

    # Filter the DataFrame for the given stop_id
    filtered_df = stop_times_df.loc[stop_times_df['stop_id'] == target_stop_id].copy()

    # Convert the arrival_time to datetime.time format
    filtered_df.loc[:, 'arrival_time'] = pd.to_datetime(filtered_df['arrival_time'], format='%H:%M:%S').dt.time

    # Get the current time with hours, minutes, and seconds
    current_time = datetime.now().strftime('%H:%M:%S')
    current_time = datetime.strptime(current_time, '%H:%M:%S').time()
    current_date = datetime.today().strftime('%Y-%m-%d')

    # Find the closest arrival time to the current time
    closest_row = filtered_df.iloc[(filtered_df['arrival_time'].apply(lambda x: time_diff(x, current_time))).argsort()[:1]]

    # Get the trip_id and arrival_time of the closest row
    closest_trip_id = closest_row['trip_id'].values[0]
    closest_arrival_time = closest_row['arrival_time'].values[0]

    # Find & print what stop we're at 
    stops_df = pd.read_csv('gtfs-static/stops.txt')

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
            if trip_update.trip.route_id == target_route_id:
                for stop_time_update in trip_update.stop_time_update:
                    if stop_time_update.stop_id == target_stop_id:
                        actual_trip_id = trip_update.trip.trip_id          
                        if stop_time_update.HasField('arrival'):
                            real_arrival_time = stop_time_update.arrival.time
                            
                            # Convert the Unix timestamp to a datetime object
                            real_arrival_time = datetime.fromtimestamp(real_arrival_time)

                            print(f"Realtime Arrival: {real_arrival_time.strftime('%H:%M:%S')}") # %Y-%m-%d 
                            # print(real_arrival_time.type())
                            print(f"Expected Arrival: {closest_arrival_time}")
                        else:
                            print("No departure time available")
    # Calculate how late/early the bus was
    diff_seconds = time_diff(real_arrival_time, closest_arrival_time)
    diff_mins = round((diff_seconds/60), 2)

    # isolate time from real_arrival_time
    real_arrival_time = real_arrival_time.time()

    results_df = pd.DataFrame(
        {
            'route_id': [target_route_id],
            'trip_id': [actual_trip_id],
            'stop_id': [target_stop_id],
            'stop_name': [stop_name.iloc[0]],
            'closest_arrival_time': [closest_arrival_time],
            'real_arrival_time' : [real_arrival_time],
            'diff_mins' : [diff_mins],
            'current_time': [current_time], 
            'current_date': [current_date]
        }
    )

    # Define the path to the results CSV file
    results_csv = 'csv/rte_19.csv'

    # Check if the file exists
    if os.path.exists(results_csv):
        # Append the new data to the existing file without writing the header
        results_df.to_csv(results_csv, mode='a', header=False, index=False)
    else:
        # Write the new data to the file, including the header
        results_df.to_csv(results_csv, mode='w', header=True, index=False)

