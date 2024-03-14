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


@app.route('/', methods=['GET', 'POST'])
def home():
    authorization_url = f"https://www.strava.com/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&response_type=code&scope={scopes}"
    if request.method == 'GET':
        return redirect(authorization_url)

@app.route('/input', methods=['GET', 'POST'])
def input_form():

    if request.method == 'POST':
        days_back = request.form.get('days_back')
        print(f"Redirecting to dashboard with, days_back: {days_back}")
        return redirect(url_for('dashboard', days_back=days_back))

    return render_template('input_form.html')

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if request.method == 'GET':
        # Retrieve parameters from the query string for GET requests
        days_back = int(request.args.get('days_back'))

        print(f"Generating plot for days_back: {days_back}")

        # Generate the plot using the generate_plot function
        fig, elevation_fig = generate_plot(days_back)

        # Check if the figure is None
        if fig is not None:
            # Convert the plot to standalone HTML
            plot_data_json = fig.to_json()
            elevation_fig_json = elevation_fig.to_json()

            return render_template('dashboard.html', plot=plot_data_json, new_plot=elevation_fig_json)
        else:
            # Handle the case where the figure is None (add your own logic)
            return render_template('error.html', message='Failed to generate plot')

    return render_template('input_form.html')



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
        session['access_token'] = access_token
        print(f"Access Token: {access_token}")

        # Store the access token in the session
        session['access_token'] = access_token

        # Redirect to the input form
        return redirect(url_for('input_form'))

    except requests.exceptions.HTTPError as e:
        return f"Error: {e.response.status_code}, {e.response.text}"
    except Exception as e:
        return f"An unexpected error occurred: {e}"



if __name__ == '__main__':
    app.run(port=3000, debug = True)
