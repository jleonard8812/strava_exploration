import requests
from creds import access_token, athlete_id

# Strava API endpoint for getting athlete activities
api_url = f'https://www.strava.com/api/v3/athletes/{athlete_id}/activities'

# Set up headers with the access token
headers = {'Authorization': f'Bearer {access_token}'}

try:
    print("Sending request to Strava API...")
    # Make a GET request to the Strava API to get athlete activities
    response = requests.get(api_url, headers=headers)

    # Print response status code and data
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Data: {response.text}")

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print("API request successful. Processing data...")
        # Convert the response to JSON
        data = response.json()

        # Filter and print information about trail run activities
        for activity in data:
            if activity['type'] == 'Run' and 'Trail' in activity.get('name', '').lower():
                print(f"Activity ID: {activity['id']}")
                print(f"Name: {activity['name']}")
                print(f"Type: {activity['type']}")
                print(f"Distance: {activity['distance']} meters")
                print(f"Start Date: {activity['start_date']}")
                print("-----")

    else:
        # Print an error message if the request was not successful
        print(f"Error: {response.status_code}, {response.text}")

except Exception as e:
    print(f"An error occurred: {e}")
