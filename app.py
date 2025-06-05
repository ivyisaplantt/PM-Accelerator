from flask import Flask, render_template, request
import requests
import os
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    error = None

    if request.method == "POST":
        location = request.form.get("location")
        if not location:
            error = "Please enter a valid city or zip code."
        else:
            url = f"https://api.openweathermap.org/data/2.5/weather"
            params = {
                "q": location,
                "appid": API_KEY,
                "units": "metric"
            }
            res = requests.get(url, params=params)
            if res.status_code == 200:
                data = res.json()
                weather_data = {
                    "location": data["name"],
                    "description": data["weather"][0]["description"].capitalize(),
                    "temperature": data["main"]["temp"]
                }
            else:
                error = "Could not retrieve weather data. Please try again."

    return render_template("index.html", weather=weather_data, error=error)

if __name__ == "__main__":
    app.run(debug=True)
