from flask import Flask, jsonify, Response
import datetime
from icalendar import Calendar, Event
from btc_halving_estimator import estimate_next_halving_date

app = Flask(__name__)

SECONDS_IN_24_HOURS = 86400
MAX_HALVINGS = 64
HALVING_INTERVAL = 210000


def calculate_halving_blocks():
    # Calculate the block heights at which halvings occur
    return [HALVING_INTERVAL * i for i in range(1, MAX_HALVINGS + 1)]


# Store the halving blocks globally
global halving_blocks
halving_blocks = calculate_halving_blocks()


@app.route("/", methods=["GET"])
@app.route("/btc-halving-date", methods=["GET"])
def btc_halving_date():
    # Endpoint to get the estimated date of the next halving event
    halving_date = estimate_next_halving_date()
    if halving_date:
        return jsonify({"halving_date": halving_date.isoformat()})
    else:
        return jsonify({"error": "Could not estimate the next Bitcoin halving date."}), 500


@app.route("/btc-halving-ical", methods=["GET"])
@app.route("/ical", methods=["GET"])
def btc_halving_ical():
    # Endpoint to generate an iCal file with future halving events
    # Retrieve the next halving date
    next_halving_date = estimate_next_halving_date()
    if not next_halving_date:
        return jsonify({"error": "Could not estimate the next Bitcoin halving date."}), 500

    # Create an iCal calendar
    cal = Calendar()
    cal.add("prodid", "-//Bitcoin Halving Calendar//example.com//")
    cal.add("version", "2.0")

    # Calculate future halvings and add them to the calendar
    for i, halving_block in enumerate(halving_blocks):
        if halving_block * HALVING_INTERVAL > next_halving_date:
            remaining_seconds = (halving_block * HALVING_INTERVAL - next_halving_date.timestamp()) * SECONDS_IN_24_HOURS
            halving_date = datetime.datetime.now() + datetime.timedelta(seconds=remaining_seconds)

            # Create an iCal event for each halving
            event = Event()
            event.add(
                "summary", f"Bitcoin Halving {i + 1}")
            event.add("dtstart", halving_date)
            event.add("dtend", halving_date + datetime.timedelta(hours=1))
            cal.add_component(event)

    # Return the iCal file as a response
    response = Response(cal.to_ical(), mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=bitcoin_halvings.ics"
    return response


if __name__ == "__main__":
    app.run(debug=True)
