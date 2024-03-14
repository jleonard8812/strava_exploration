import requests
import json
import pandas as pd
import plotly.express as px
from flask import session

def generate_plot(days_back=30, activity_type='Run'):
    # Check if access token exists in the session
    access_token = session.get('access_token')

    if not access_token:
        return "Error: Access token not found in session. User not authenticated."
    
    # Strava API endpoint for getting athlete activities
    api_url = 'https://www.strava.com/api/v3/athlete/activities'

    # Set up headers with the access token
    headers = {'Authorization': f'Bearer {access_token}'}

    # Calculate the end date based on the days_back parameter
    end_date = pd.Timestamp.now().normalize()
    start_date = end_date - pd.DateOffset(days=days_back)

    # Initialize an empty DataFrame to store all activities
    all_activities_df = pd.DataFrame()
    # Parameters for the API request
    page_num = 1

    try:
        print("Sending request to Strava API...")
        while True:
            # Parameters for the API request
            params = {
                'per_page': 200,
                'before': int(end_date.timestamp()),  # Convert to Unix timestamp
                'after': int(start_date.timestamp()),  # Convert to Unix timestamp
                'page': page_num
            }

            # Make a GET request to the Strava API to get athlete activities
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()

            # Print response status code
            print(f"Response Status Code: {response.status_code}")

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                print("API request successful. Processing data...")
                # Convert the response to JSON
                data = response.json()
                 # If the response data is empty, break the loop
                if not data:
                    print("No more data to return, breaking loop")
                    break

                # Create a DataFrame from the JSON data
                df = pd.json_normalize(data)
                
                # Filter activities by type
                if activity_type:
                    df = df[df['type'] == activity_type]

                print("Total number of activities returned:", len(df))
                
                # Filter out activities with missing heart rate
                df = df.dropna(subset=['average_heartrate'])

                # Concatenate the DataFrame to the all_activities_df
                all_activities_df = pd.concat([all_activities_df, df], ignore_index=True)

                # Increment page number for the next request
                page_num += 1

               

            else:
                # Print an error message if the request was not successful
                print(f"Error: {response.status_code}, {response.text}")
                break

        # Process the concatenated DataFrame
        trail_runs = all_activities_df.copy()
        trail_runs['start_date'] = pd.to_datetime(trail_runs['start_date'])
        trail_runs['total_elevation_gain'] *= 3.28084
        trail_runs['average_speed'] *= 2.23694

        print("Creating scatter plot...")
        # Create a figure with two y-axes
        fig = px.scatter(
            trail_runs,
            x='total_elevation_gain',
            y='average_speed',
            title='Elevation Gain vs Speed with Heart Rate',
            labels={'total_elevation_gain': 'Total Elevation Gain (ft)', 'average_speed': 'Average Speed (mph)'},
            color='average_heartrate',
            size='average_heartrate',
            hover_data=['start_date', 'name'],
            color_continuous_scale='bluered',
        )

        print("Creating histogram...")            
        elevation_hist = px.histogram(
            trail_runs,
            x='total_elevation_gain',
            title='Elevation Gain Distribution',
            labels={'total_elevation_gain': 'Total Elevation Gain (ft)', 'count': '# of Runs'},
            nbins=20
        )
        elevation_hist.update_yaxes(title_text='Number of Runs')

        print("Creating calorie scatter plot...")
        # Create a figure with two y-axes
        calorie_fig = px.scatter(
            trail_runs,
            x='distance',
            y='average_speed',
            title='Calories Burned vs Speed and Distance',
            labels={'distance': 'Distance (miles)', 'average_speed': 'Average Speed (mph)', 'calories': 'Calories Burned'},
            color='calories',
            size='calories',
            hover_data=['start_date', 'name'],
            color_continuous_scale='bluered',
        )


        return fig, elevation_hist, calorie_fig

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}, {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
