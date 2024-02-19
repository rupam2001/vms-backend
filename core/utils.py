from datetime import datetime, timedelta
from django.utils import timezone

def add_hours_to_utc(utc_time_str, hours_to_add):
    # Convert the UTC time string to a datetime object
    utc_datetime = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%S.%fZ')

    # Add the specified number of hours
    updated_utc_datetime = utc_datetime + timedelta(hours=hours_to_add)

    # Convert the updated datetime object back to a UTC time string
    updated_utc_time_str = updated_utc_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'

    return updated_utc_time_str

def get_currenttime_utc():
    return timezone.now().date()
