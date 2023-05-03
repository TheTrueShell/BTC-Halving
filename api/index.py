from flask import Flask, jsonify, Response
import requests
import datetime
from icalendar import Calendar, Event

app = Flask(__name__)

BLOCKCHAIR_API_URL = "https://api.blockchair.com/bitcoin/stats"
HALVING_INTERVAL = 210000
SECONDS_IN_24_HOURS = 86400
MAX_HALVINGS = 64


def calculate_halving_blocks():
    return [HALVING_INTERVAL * i for i in range(1, MAX_HALVINGS + 1)]


global halving_blocks
halving_blocks = calculate_halving_blocks()


def get_blockchain_stats():
    response = requests.get(BLOCKCHAIR_API_URL)
    data = response.json()
    return data["data"]


def calculate_average_block_time(stats):
    blocks_24h = stats["blocks_24h"]
    return SECONDS_IN_24_HOURS / blocks_24h


def calculate_halving_date(current_block_height, average_block_time):
    for halving_block in halving_blocks:
        if halving_block > current_block_height:
            remaining_blocks = halving_block - current_block_height
            remaining_seconds = remaining_blocks * average_block_time
            return datetime.datetime.now() + datetime.timedelta(seconds=remaining_seconds)

@app.route("/", methods=["GET"])
@app.route("/btc-halving-date", methods=["GET"])
def btc_halving_date():
    stats = get_blockchain_stats()
    current_block_height = stats["blocks"]
    average_block_time = calculate_average_block_time(stats)
    halving_date = calculate_halving_date(
        current_block_height, average_block_time)
    return jsonify({"halving_date": halving_date.isoformat()})


@app.route("/btc-halving-ical", methods=["GET"])
@app.route("/ical", methods=["GET"])
def btc_halving_ical():
    stats = get_blockchain_stats()
    current_block_height = stats["blocks"]
    average_block_time = calculate_average_block_time(stats)

    # Create an iCal calendar
    cal = Calendar()
    cal.add("prodid", "-//Bitcoin Halving Calendar//example.com//")
    cal.add("version", "2.0")

    # Calculate future halvings and add them to the calendar
    for halving_block in halving_blocks:
        if halving_block > current_block_height:
            remaining_blocks = halving_block - current_block_height
            remaining_seconds = remaining_blocks * average_block_time
            halving_date = datetime.datetime.now() + datetime.timedelta(seconds=remaining_seconds)

            event = Event()
            event.add(
                "summary", f"Bitcoin Halving {len(cal.subcomponents) + 1}")
            event.add("dtstart", halving_date)
            event.add("dtend", halving_date + datetime.timedelta(hours=1))
            cal.add_component(event)

    # Return the iCal file
    response = Response(cal.to_ical(), mimetype="text/calendar")
    response.headers["Content-Disposition"] = "attachment; filename=bitcoin_halvings.ics"
    return response


if __name__ == "__main__":
    app.run(debug=True)
