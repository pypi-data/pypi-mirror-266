from datetime import datetime, timedelta
import uuid
import time
import random

def ts_to_datetime(timestamp_ms):
    timestamp_seconds = timestamp_ms / 1000
    dateTimeObj = datetime.fromtimestamp(timestamp_seconds)
    return dateTimeObj.strftime("%Y-%m-%d %H:%M:%S")

def get_uuid():
    return str(uuid.uuid4())

def get_random_int():
    return random.randint(1, 9000000)

def get_curr_timestamp_ms():
    return int(time.time() * 1000)

def get_1d_ago_ts_ms():
    current_timestamp = datetime.now()
    timestamp_day_before = current_timestamp - timedelta(days=1)
    return int(timestamp_day_before.timestamp())

def datetime_to_ts_ms(datetime_str):
    datetime_obj = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    return int(datetime_obj.timestamp() * 1000)