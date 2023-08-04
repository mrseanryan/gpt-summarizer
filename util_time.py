from datetime import timedelta
import time

def start_timer():
    return time.time()

def end_timer(start):
    end = time.time()
    seconds_elapsed = end - start
    return seconds_elapsed

def describe_elapsed_seconds(seconds_elapsed):
    if seconds_elapsed is None:
        return "(unknown)"
    return f"{timedelta(seconds=seconds_elapsed)}s"
