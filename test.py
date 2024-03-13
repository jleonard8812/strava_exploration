import requests
from creds import access_token, athlete_id
from generate_histo import generate_histo

gen = generate_histo(25)


# # Strava API endpoint for getting activities
# api_url = f'https://www.strava.com/api/v3/athletes/{athlete_id}'

# # Set up headers with the access token
# headers = {'Authorization': f'Bearer {access_token}'}

# try:
#     # Make a GET request to the Strava API
#     response = requests.get(api_url, headers=headers)

#     # Check if the request was successful (status code 200)
#     if response.status_code == 200:
#         try:
#             # Convert the response to JSON
#             data = response.json()

#             # Print some information about the athlete
#             print(f"Athlete ID: {data['id']}")
#             print(f"Athlete Name: {data['firstname']} {data['lastname']}")
#             print(f"Athlete Username: {data['username']}")
#             print(f"Athlete Email: {data['email']}")
#             print(f"Athlete Profile: {data['profile']}")
#             print("-----")

#         except ValueError as json_error:
#             print(f"JSON decoding error: {json_error}")
#     else:
#         # Print an error message if the request was not successful
#         print(f"Error: {response.status_code}, {response.text}")

# except Exception as e:
#     print(f"An error occurred: {e}")

# # create a server
#     # python -m http.server 3000

# # reathorize website if needed:
# # https://www.strava.com/oauth/authorize?client_id=122789&redirect_uri=http://localhost:3000&response_type=code&scope=read,activity:read_all&approval_prompt=auto
