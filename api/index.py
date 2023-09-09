from flask import Flask, jsonify, Response
import datetime
import logging
from icalendar import Calendar, Event
from btc_halving_estimator import estimate_next_halving_date, get_average_block_time

BTC_HALVING_INTERVAL = 210000

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/btc-halving-date", methods=["GET"])
def btc_halving_date():
    next_halving_date, _ = estimate_next_halving_date()
    if next_halving_date:
        return jsonify({"halving_date": next_halving_date.isoformat()})
    else:
        return jsonify({"error": "Could not estimate the next Bitcoin halving date."}), 500


@app.route("/btc-halving-ical", methods=["GET"])
@app.route("/ical", methods=["GET"])
def btc_halving_ical():
    next_halving_date, current_block_height = estimate_next_halving_date()
    if not next_halving_date:
        return jsonify({"error": "Could not estimate the next Bitcoin halving date."}), 500

    logging.info(f"Next halving date estimated to be: {next_halving_date}")

    # Create an iCal calendar
    cal = Calendar()
    cal.add("prodid", "-//Bitcoin Halving Calendar//btc.biotic.win//")
    cal.add("version", "2.0")

    # Time interval between each halving (in seconds)
    # This is an estimate and should be refined based on more accurate data
    estimated_halving_interval = BTC_HALVING_INTERVAL * get_average_block_time(current_block_height)

    # Create an iCal event for the next 5 halvings
    for i in range(5):
        halving_date = next_halving_date + datetime.timedelta(seconds=i * estimated_halving_interval)
        event = Event()
        event.add("summary", f"Bitcoin Halving {i + 1}")
        event.add("dtstart", halving_date)
        event.add("dtend", halving_date + datetime.timedelta(hours=1))
        cal.add_component(event)

    # Return the iCal file as a response
    response = Response(cal.to_ical(), mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=bitcoin_halvings.ics"
    return response


if __name__ == "__main__":
    app.run(debug=True)
