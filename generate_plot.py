import requests
import json
import pandas as pd
import plotly.express as px
from flask import session

def generate_plot(days_back):
    # Check if access token exists in the session
    access_token = session.get('access_token')

    if not access_token:
        return "Error: Access token not found in session. User not authenticated."
    # Strava API endpoint for getting athlete activities
    api_url = 'https://www.strava.com/api/v3/athlete/activities?per_page=200'

    # Set up headers with the access token
    headers = {'Authorization': f'Bearer {access_token}'}

    # Set days back variable
    if days_back <= 0:
        days_back = (pd.to_datetime('today') - pd.DateOffset(days=30)).tz_localize(None)
    else:
        days_back = (pd.to_datetime('today') - pd.DateOffset(days=days_back)).tz_localize(None)

    try:
        print("Sending request to Strava API...")
        # Make a GET request to the Strava API to get athlete activities
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()

        # Print response status code
        print(f"Response Status Code: {response.status_code}")

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            print("API request successful. Processing data...")
            # Convert the response to JSON
            data = response.json()

            # Create a DataFrame from the JSON data
            df = pd.json_normalize(data)

            # Filter for trail runs and activities within the last 2 years
            trail_runs = df[(df['type'] == 'Run') & (df['name'].str.contains('Trail', case=False, na=False))]
            trail_runs['start_date'] = pd.to_datetime(trail_runs['start_date'])
            trail_runs_2_years = trail_runs[
                trail_runs['start_date'].dt.tz_localize(None) >= days_back
            ].copy()  # Use .copy() to avoid SettingWithCopyWarning

            print(f"Number of rows in trail_runs_2_years: {len(trail_runs_2_years)}")
            print(f"Head of trail_runs_2_years:\n{trail_runs_2_years.head()}")

            trail_runs_2_years.loc[:, 'total_elevation_gain'] *= 3.28084
            trail_runs_2_years.loc[:, 'average_speed'] *= 2.23694

            print("Creating scatter plot...")
            # Create a figure with two y-axes
            fig = px.scatter(
                trail_runs_2_years,
                x='average_speed',
                y='total_elevation_gain',
                title='Elevation Gain vs Speed with Heart Rate',
                labels={'total_elevation_gain': 'Total Elevation Gain (ft)', 'average_speed': 'Average Speed (mph)'},
                color='average_heartrate',
                size='average_heartrate',
                hover_data=['start_date', 'name'],
                color_continuous_scale='bluered',
            )
            print(f"Type of object returned: {type(fig)}")
            return fig

        else:
            # Print an error message if the request was not successful
            print(f"Error: {response.status_code}, {response.text}")

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}, {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

