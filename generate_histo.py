import requests
import json
import pandas as pd
import plotly.express as px
from flask import session

def generate_histo(days_back):
    # Check if access token exists in the session
    access_token = session.get('access_token')

    if not access_token:
        return "Error: Access token not found in session. User not authenticated."
    
    # Strava API endpoint for getting athlete activities
    api_url = 'https://www.strava.com/api/v3/athlete/activities'
    
    # Set up headers with the access token
    headers = {'Authorization': f'Bearer {access_token}'}
    
    # Set days back variable
    if days_back <= 0:
        days_back = (pd.to_datetime('today') - pd.DateOffset(days=30)).tz_localize(None)
    else:
        days_back = (pd.to_datetime('today') - pd.DateOffset(days=days_back)).tz_localize(None)
    
    all_activities = []
    page = 1
    per_page = 200  # Maximum per_page value allowed by Strava API
    
    try:
        while True:
            print(f"Sending request to Strava API for page {page}...")
            # Make a GET request to the Strava API to get athlete activities
            params = {'per_page': per_page, 'page': page}
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
    
            # Print response status code
            print(f"Response Status Code: {response.status_code}")
    
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                print("API request successful. Processing data...")
                # Convert the response to JSON
                data = response.json()
    
                # Add activities to the list
                all_activities.extend(data)
    
                # Print number of activities fetched in this page
                print(f"Activities fetched in page {page}: {len(data)}")
    
                # Check if there are more pages
                if len(data) < per_page:
                    break  # No more pages, exit loop
    
                # Increment page number for next request
                page += 1
    
        print(f"Total activities fetched: {len(all_activities)}")
        
        # Process all_activities as needed
        # For example, convert to DataFrame and filter
        df = pd.json_normalize(all_activities)
        # Filter for trail runs and activities within the specified date range
        trail_runs = df[(df['type'] == 'Run') & (df['name'].str.contains('Trail', case=False, na=False))]
        trail_runs['start_date'] = pd.to_datetime(trail_runs['start_date'])
        trail_runs_2_years = trail_runs[
            trail_runs['start_date'].dt.tz_localize(None) >= days_back
        ].copy()  # Use .copy() to avoid SettingWithCopyWarning

        print(f"Number of rows in histo: {len(trail_runs_2_years)}")
        
        trail_runs_2_years.loc[:, 'total_elevation_gain'] *= 3.28084
        trail_runs_2_years.loc[:, 'average_speed'] *= 2.23694

        print("Creating histogram...")            
        elevation_hist = px.histogram(
            trail_runs_2_years,
            x='total_elevation_gain',
            title='Elevation Gain Distribution',
            labels={'total_elevation_gain': 'Total Elevation Gain (ft)', 'count': '# of Runs'},
            nbins=20 )
        elevation_hist.update_yaxes(title_text='Number of Runs')

        return elevation_hist

    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e.response.status_code}, {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
