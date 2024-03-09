from flask import Flask, request, redirect, render_template, url_for
import requests
import os
from creds import client_id, client_secret, redirect_uri, scopes
import plotly.express as px
from generate_plot import generate_plot 
import plotly.io as pio

app = Flask(__name__)

# Define a global variable to store athlete_id temporarily
temp_athlete_id = None

@app.route('/')
def home():
    authorization_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&approval_prompt=auto"
    return f"Visit the following URL to authorize the application: <a href='{authorization_url}'>{authorization_url}</a>"

@app.route('/input', methods=['GET', 'POST'])
def input_form():
    global temp_athlete_id

    if request.method == 'POST':
        temp_athlete_id = request.form.get('athlete_id')
        days_back = request.form.get('days_back')
        print(f"Redirecting to dashboard with athlete_id: {temp_athlete_id}, days_back: {days_back}")
        return redirect(url_for('dashboard', athlete_id=temp_athlete_id, days_back=days_back))

    return render_template('input_form.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    global temp_athlete_id

    if request.method == 'POST':
        # Retrieve the desired time range and athlete_id from the form
        days_back = int(request.form.get('days_back'))
        athlete_id = temp_athlete_id

        print(f"Generating plot for athlete_id: {athlete_id}, days_back: {days_back}")

        # Generate the plot using the generate_plot function
        fig = generate_plot(athlete_id, days_back)

        # Convert the plot to standalone HTML
        plot_html = pio.to_html(fig, full_html=False)

        return render_template('dashboard.html', plot=plot_html)

    elif request.method == 'GET':
        # Retrieve parameters from the query string for GET requests
        days_back = int(request.args.get('days_back'))
        athlete_id = temp_athlete_id

        print(f"Generating plot for athlete_id: {athlete_id}, days_back: {days_back}")

        # Generate the plot using the generate_plot function
        fig = generate_plot(athlete_id, days_back)

        # Convert the plot to standalone HTML
        plot_html = pio.to_html(fig, full_html=False)

        return render_template('dashboard.html', plot=plot_html)

    return render_template('input_form.html', athlete_id=temp_athlete_id)


@app.route('/callback')
def callback():
    authorization_code = request.args.get('code')
    print(f"Authorization Code: {authorization_code}")

    token_url = "https://www.strava.com/oauth/token"

    token_data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": authorization_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }

    try:
        response = requests.post(token_url, data=token_data)
        response.raise_for_status()

        access_token = response.json().get("access_token")
        print(f"Access Token: {access_token}")

        # Check if creds.py is writable
        creds_file_path = 'creds.py'
        print(f"Creds File Path: {os.path.abspath(creds_file_path)}")  # Print the absolute path
        print(f"Creds File Writable: {os.access(creds_file_path, os.W_OK)}")  # Print if the file is writable

        if os.access(creds_file_path, os.W_OK):
            # Save the access token to creds.py
            with open(creds_file_path, 'a') as creds_file:
                creds_file.write(f"access_token = '{access_token}'\n")

            # Redirect to the input form
            return redirect(url_for('input_form'))

        else:
            return "Error: creds.py is not writable."

    except requests.exceptions.HTTPError as e:
        return f"Error: {e.response.status_code}, {e.response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == '__main__':
    app.run(port=3000)
