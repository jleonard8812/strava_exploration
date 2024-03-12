from flask import Flask, request, redirect, render_template, url_for, session
import requests
import os
from creds import client_id, client_secret, redirect_uri, scopes
import plotly.express as px
from generate_plot import generate_plot 
import plotly.io as pio
import plotly.offline as pyo
from flask_session import Session 
import json
import plotly


app = Flask(__name__,)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'your_secret_key_here'
Session(app) 

# Define a global variable to store athlete_id temporarily

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        print("Received POST request") 
        athlete_id = request.form.get('athlete_id')
        session['athlete_id'] = athlete_id

        # Construct the authorization URL with the correct client_id
        authorization_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}&approval_prompt=auto&state={athlete_id}"

        print(f"Authorization URL: {authorization_url}")  # Print for debugging

        # Redirect the user to the authorization URL
        return redirect(authorization_url)

    return render_template('home.html')

@app.route('/input', methods=['GET', 'POST'])
def input_form():

    if request.method == 'POST':
        # temp_athlete_id = request.form.get('athlete_id')
        days_back = request.form.get('days_back')
        athlete_id = session.get('athlete_id')
        print(f"input URL athlete_id : {athlete_id}")
        print(f"Redirecting to dashboard with athlete_id: {athlete_id}, days_back: {days_back}")
        return redirect(url_for('dashboard', athlete_id=athlete_id, days_back=days_back))

    return render_template('input_form.html')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if request.method == 'POST':
        # Retrieve the desired time range and athlete_id from the form
        days_back = int(request.form.get('days_back'))
        athlete_id = session.get('athlete_id')
        print(f"dashboard URL athlete_id : {athlete_id}")

        print(f"Generating plot for athlete_id: {athlete_id}, days_back: {days_back}")

        # Generate the plot using the generate_plot function
        fig = generate_plot(athlete_id, days_back)
        print(f"Type of object returned: {type(fig)}")

        # Check if the figure is None
        if fig is not None:
            # Convert the plot to standalone HTML
            plot_html = pio.to_html(fig, full_html=False)
            plot_data_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            print(f"Type of plot_html object returned: {type(plot_html)}")
            return render_template('dashboard.html', plot=plot_html, plot_json=plot_data_json)
        else:
            # Handle the case where the figure is None (add your own logic)
            return render_template('error.html', message='Failed to generate plot')

    elif request.method == 'GET':
        # Retrieve parameters from the query string for GET requests
        days_back = int(request.args.get('days_back'))
        athlete_id = session.get('athlete_id')

        print(f"Generating plot for athlete_id: {athlete_id}, days_back: {days_back}")

        # Generate the plot using the generate_plot function
        fig = generate_plot(athlete_id, days_back)
        print(f"Type of object returned: {type(fig)}")
        # Check if the figure is None
        if fig is not None:
            # Convert the plot to standalone HTML
            plot_data_json = fig.to_json()

            return render_template('dashboard.html', plot=plot_data_json)
        else:
            # Handle the case where the figure is None (add your own logic)
            return render_template('error.html', message='Failed to generate plot')

    return render_template('input_form.html', athlete_id=athlete_id)


@app.route('/callback')
def callback():
    authorization_code = request.args.get('code')
    athlete_id = request.args.get('state')
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
                session['athlete_id'] = athlete_id

            # Redirect to the input form
            return redirect(url_for('input_form'))

        else:
            return "Error: creds.py is not writable."

    except requests.exceptions.HTTPError as e:
        return f"Error: {e.response.status_code}, {e.response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"


if __name__ == '__main__':
    app.run(port=3000, debug = True)
