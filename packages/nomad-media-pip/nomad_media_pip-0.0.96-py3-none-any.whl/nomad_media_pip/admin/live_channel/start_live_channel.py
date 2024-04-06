from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.live_channel.live_channel_statuses import _LIVE_CHANNEL_STATUSES
from nomad_media_pip.admin.live_channel.wait_for_live_channel_status import _wait_for_live_channel_status

import json, requests

def _start_live_channel(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG):
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/start"

    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if (DEBUG):
        print(f"API_URL: {API_URL}\nMETHOD: POST")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS)

        # Wait for the Live Channel to be running
        _wait_for_live_channel_status(AUTH_TOKEN, URL, CHANNEL_ID, _LIVE_CHANNEL_STATUSES["Running"], 1200, 20, DEBUG)

    except:
        _api_exception_handler(RESPONSE, f"Start Live Channel {CHANNEL_ID} failed")

