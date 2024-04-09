import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

MAX_RETRIES = 2


class LogRetry(Retry):
    """
    Adding extra logs before making a retry request
    """

    def __init__(self, total, *args, **kwargs):
        super().__init__(total, *args, **kwargs)
        # Total is the number of retries remaining. Starts at MAX_RETRIES and counts down to zero.
        if total < MAX_RETRIES:
            logging.info(f"Retry attempt number: {MAX_RETRIES - total}")


def create_session():
    session = requests.Session()
    retries = LogRetry(
        total=MAX_RETRIES,
        # Enable exponential back-off
        backoff_factor=1,
        # Retry for these statuses
        status_forcelist=[
            429,  # Too many requests
            500,  # Internal Server Error
            502,  # Bad Gateway
            503,  # Service Unavailable
            504,  # Gateway Timeout
        ],
        # Retry on connection errors
        connect=MAX_RETRIES,
        # Retry on read errors
        read=MAX_RETRIES,
        # Don't retry on redirect (default)
        redirect=None,
        # Retry on errors other than connection, read, redirect or status.
        other=MAX_RETRIES,
    )

    session.mount("http://", HTTPAdapter(max_retries=retries))
    session.mount("https://", HTTPAdapter(max_retries=retries))

    return session
