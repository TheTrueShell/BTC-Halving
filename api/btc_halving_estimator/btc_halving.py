import requests
import datetime
import logging
from dateutil.parser import parse

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Constants
BTC_HALVING_INTERVAL = 210000
BLOCKCHAIR_API_URL = "https://api.blockchair.com/bitcoin/blocks"


def get_latest_block_data():
    logging.info("Fetching the latest block data")
    try:
        response = requests.get(BLOCKCHAIR_API_URL + "?limit=1")
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching the latest block data: {e}")
        return None

    data = response.json().get('data')
    if data:
        logging.info(f"Latest block data: {data[0]}")
        return data[0]
    logging.warning("No data found for the latest block")
    return None


def get_average_block_time(current_block_height):
    logging.info("Calculating the average block time")
    
    # Dynamically set the number of blocks for averaging based on how close the halving is
    blocks_to_halving = BTC_HALVING_INTERVAL - (current_block_height % BTC_HALVING_INTERVAL)
    if blocks_to_halving > 10000:
        num_blocks = 100
    else:
        num_blocks = 50
    
    request_url = f"{BLOCKCHAIR_API_URL}?s=time(desc)&limit={num_blocks}"
    
    logging.info(f"Requesting data from: {request_url}")

    try:
        response = requests.get(request_url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching block data: {e}")
        return 600  # fallback to 10 minutes

    data = response.json().get('data')
    if data and len(data) > 1:
        total_weight = 0
        total_time = 0

        # Weighted average, more recent blocks are given higher weight
        for i, block in enumerate(data[:-1]):
            block_time = parse(block['time'])
            next_block_time = parse(data[i + 1]['time'])
            weight = i + 1
            total_weight += weight
            total_time += weight * (block_time - next_block_time).total_seconds()

        avg_block_time = total_time / total_weight
        logging.info(f"Weighted average block time: {avg_block_time} seconds")
        return avg_block_time

    logging.warning("Could not calculate average block time")
    return 600  # fallback to 10 minutes


def calculate_next_halving_date(current_block_height, current_block_time, avg_block_time):
    logging.info("Calculating the next halving date")
    
    blocks_remaining = BTC_HALVING_INTERVAL - (current_block_height % BTC_HALVING_INTERVAL)
    logging.info(f"Blocks remaining until next halving: {blocks_remaining}")

    latest_block_time = parse(current_block_time)
    
    seconds_remaining = blocks_remaining * avg_block_time
    next_halving_date = latest_block_time + datetime.timedelta(seconds=seconds_remaining)
    logging.info(f"Next halving date estimated to be: {next_halving_date}")
    
    return next_halving_date


def estimate_next_halving_date():
    latest_block_data = get_latest_block_data()
    
    if latest_block_data:
        average_block_time = get_average_block_time(latest_block_data['id'])
        return calculate_next_halving_date(
            latest_block_data['id'], latest_block_data['time'], average_block_time
        )
    return None


if __name__ == "__main__":
    # Run the function and print the estimated date of the next Bitcoin halving
    next_halving_date = estimate_next_halving_date()
    if next_halving_date:
        print(f"The estimated date of the next Bitcoin halving is: {next_halving_date}")
    else:
        print("Could not estimate the date of the next Bitcoin halving")
