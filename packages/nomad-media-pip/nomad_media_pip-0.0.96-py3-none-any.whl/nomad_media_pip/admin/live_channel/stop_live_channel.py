from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.live_channel.live_channel_statuses import _LIVE_CHANNEL_STATUSES
from nomad_media_pip.admin.live_channel.wait_for_live_channel_status import _wait_for_live_channel_status

import json, requests

def _stop_live_channel(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG):
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/stop"

    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if (DEBUG):
        print(f"API_URL: {API_URL}\nMETHOD: POST")

    # Send the request
    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS)

        # Wait for the live channel to be idle
        _wait_for_live_channel_status(AUTH_TOKEN, URL, CHANNEL_ID, _LIVE_CHANNEL_STATUSES["Idle"], 120, 2, DEBUG)

    except:
        _api_exception_handler(RESPONSE, "Stop Live Channel " + CHANNEL_ID + " failed")

