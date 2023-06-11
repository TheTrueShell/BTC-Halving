from btc_halving_estimator import estimate_next_halving_date

next_halving_date = estimate_next_halving_date()
if next_halving_date:
    print(f"Estimated date of the next Bitcoin halving is: {next_halving_date}")
else:
    print("Could not estimate the next Bitcoin halving date.")
