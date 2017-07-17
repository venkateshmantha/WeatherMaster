import urllib, json, os, pyowm

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json()
    json.dumps(req, indent=4)
    res = processRequest(req)
    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "citynameAction":
        return {}

    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")

    owm = pyowm.OWM('7521c2b2765cf016a55b005b107ea3a7')  # You MUST provide a valid API key

    observation = owm.weather_at_place(city)
    w = observation.get_weather()
    max_temp = str(w.get_temperature('celsius')['temp_max'])
    min_temp = str(w.get_temperature('celsius')['temp_min'])
    current_temp = str(w.get_temperature('celsius')['temp'])
    status = w.get_status()
    icon = w.get_weather_icon_name()
    wind_speed = str(w.get_wind()['speed'])
    humidity = str(w.get_humidity())

    report = 'Status: ' + status + '\n' + 'Max: ' + max_temp + '\n' + 'Min: ' + min_temp + '\n' \
             + 'Current: ' + current_temp + '\n' + 'Wind speed: ' + wind_speed + '\n' + 'Humidity: ' + humidity + '%'

    title = city + " Weather Report"
    print("Weather report ", report)

    facebook_message = {
        "attachment": {
            "type": "template",
            "payload": {
                "template_type": "generic",
                "elements": [
                    {
                        "title": title,
                        "image_url": "http://openweathermap.org/img/w/" +icon + ".png",
                        "subtitle": report
                    }
                ]
            }
        }
    }

    return {
        "speech": report,
        "displayText": report,
        "data": {"facebook": facebook_message},
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':

    app.run()