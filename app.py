from flask import Flask, render_template, request, redirect, url_for
from models import db, WeatherEntry
from dotenv import load_dotenv
import requests, os

load_dotenv()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

API_KEY = os.getenv("API_KEY")

@app.before_request
def create_tables():
    db.create_all()

@app.route("/", methods=["GET", "POST"])
def index():
    weather_data = None
    forecast_data = None
    error = None

    if request.method == "POST":
        location = request.form.get("location")
        unit = request.form.get("unit") or "metric"
        unit_symbol = "°C" if unit == "metric" else "°F"
        date = request.form.get("start_date")

        if not location or not date:
            error = "Please enter both location and date."
        else:
            try:
                params = {
                    "q": location,
                    "appid": API_KEY,
                    "units": unit
                }
                current_res = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
                forecast_res = requests.get("https://api.openweathermap.org/data/2.5/forecast", params=params)

                if current_res.status_code == 200 and forecast_res.status_code == 200:
                    current = current_res.json()
                    forecast = forecast_res.json()

                    weather_data = {
                        "location": current["name"],
                        "description": current["weather"][0]["description"].capitalize(),
                        "temperature": current["main"]["temp"],
                        "unit": unit_symbol
                    }

                    forecast_data = []
                    for item in forecast["list"]:
                        if "12:00:00" in item["dt_txt"]:
                            forecast_data.append({
                                "date": item["dt_txt"].split(" ")[0],
                                "temp": item["main"]["temp"],
                                "desc": item["weather"][0]["description"].capitalize(),
                                "unit": unit_symbol
                            })

                    entry = WeatherEntry(
                        location=current["name"],
                        date=date,
                        temperature=current["main"]["temp"],
                        description=current["weather"][0]["description"].capitalize()
                    )
                    db.session.add(entry)
                    db.session.commit()
                else:
                    error = "Weather API error. Check location or try again."

            except Exception as e:
                error = str(e)

    return render_template("index.html", weather=weather_data, forecast=forecast_data, error=error)

@app.route("/read")
def read():
    entries = WeatherEntry.query.all()
    return render_template("read.html", entries=entries)

@app.route("/update/<int:id>", methods=["GET", "POST"])
def update(id):
    entry = WeatherEntry.query.get_or_404(id)
    if request.method == "POST":
        entry.location = request.form.get("location")
        entry.date = request.form.get("date")
        entry.temperature = float(request.form.get("temperature"))
        entry.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("read"))
    return render_template("update.html", entry=entry)

@app.route("/delete/<int:id>")
def delete(id):
    entry = WeatherEntry.query.get_or_404(id)
    db.session.delete(entry)
    db.session.commit()
    return redirect(url_for("read"))

if __name__ == "__main__":
    app.run(debug=True)
