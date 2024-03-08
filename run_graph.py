import requests
from creds import access_token, athlete_id
import json
import pandas as pd
import plotly.express as px

# Strava API endpoint for getting athlete activities
api_url = f'https://www.strava.com/api/v3/athletes/{athlete_id}/activities?per_page=200'

# Set up headers with the access token
headers = {'Authorization': f'Bearer {access_token}'}

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
        trail_runs = df[(df['type'] == 'Run') & (df['name'].str.contains('Trail', case=False, na=False))] #| (df['name'] == 'Leadville 100'))]
        trail_runs['start_date'] = pd.to_datetime(trail_runs['start_date'])
        trail_runs_2_years = trail_runs[
            (trail_runs['start_date'].dt.tz_localize(None) >= (pd.to_datetime('today') - pd.DateOffset(years=2)).tz_localize(None))
        ]

        # Convert elevation from meters to feet
        trail_runs_2_years['total_elevation_gain'] *= 3.28084
        # Convert meters per second to mph
        trail_runs_2_years['average_speed'] *= 2.23694
        # Create a figure with two y-axes
        fig = px.bar(
            trail_runs_2_years,
            x='start_date',
            y='average_heartrate',
            color='average_speed',
            color_continuous_scale='Plasma',
            range_x=[
                    trail_runs_2_years['start_date'].min() - pd.DateOffset(days=3),
                    trail_runs_2_years['start_date'].max() + pd.DateOffset(days=3),
                    ],  # Add padding to both sides
            title='Trail Run Metrics (Last 12 Months)',
            labels={'average_heartrate': 'Average Heart Rate', 'start_date': 'Date', 'average_speed': 'Avg Speed (Mph)'}
        )

        # Add elevation line using the second y-axis
        fig.add_trace(
            px.line(
                trail_runs_2_years,
                x='start_date',
                y='total_elevation_gain',
                color_discrete_sequence=['green'],  # Color for elevation line
                labels={'total_elevation_gain': 'Total Elevation Gain'}
            ).update_traces(yaxis='y2').data[0]
        )

        # Update layout to include a second y-axis
        fig.update_layout(
            yaxis2=dict(
                title='Total Elevation Gain (ft)',
                overlaying='y',
                side='right'
            )
        )

        # Show the figure
        fig.update_traces(marker=dict(line=dict(width=0.02))) 
        fig.update_layout(coloraxis_colorbar=dict(x=1.067))
        fig.show()

    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}, {response.text}")

except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e.response.status_code}, {e.response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
