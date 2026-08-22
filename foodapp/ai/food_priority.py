from datetime import datetime

def calculate_food_priority(expiry_time):

    now = datetime.now()

    current_minutes = (
        now.hour * 60 +
        now.minute
    )
    expiry_minutes = (
        expiry_time.hour * 60 +
        expiry_time.minute
    )
    remaining_minutes = expiry_minutes - current_minutes

    # If expiry is already passed
    if remaining_minutes <= 0:
        return "HIGH"

    if remaining_minutes <= 120:
        return "HIGH"

    elif remaining_minutes <= 360:
        return "MEDIUM"

    else:
        return "LOW"