import requests
from creds import client_id, client_secret, redirect_uri, scopes


authorization_code = '49b38ccce69c3a7244fca4d9fae186299170283c'
# Construct the authorization URL
authorization_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&approval_prompt=auto"

# Print the URL and direct the user to visit it
print("Visit the following URL to authorize the application:")
print(authorization_url)

# Construct the token endpoint URL
token_url = "https://www.strava.com/oauth/token"

# Set up the data for the token request
token_data = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": authorization_code,
    "grant_type": "authorization_code",
    "redirect_uri": redirect_uri
}

try:
    # Make the POST request to exchange authorization code for access token
    response = requests.post(token_url, data=token_data)
    response.raise_for_status()

    # Extract the access token from the response
    access_token = response.json()["access_token"]
    print(f"Access Token: {access_token}")

except requests.exceptions.HTTPError as e:
    print(f"Error: {e.response.status_code}, {e.response.text}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
