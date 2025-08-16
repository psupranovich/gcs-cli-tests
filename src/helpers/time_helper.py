import time


def get_current_epoch_time() -> int:
    """
    Returns the current time as Unix epoch timestamp.
    """
    return int(time.time()*1000)
