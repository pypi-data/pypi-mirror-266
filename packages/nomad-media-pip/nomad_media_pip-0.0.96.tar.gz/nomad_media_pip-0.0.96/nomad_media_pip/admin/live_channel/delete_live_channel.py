from nomad_media_pip.admin.live_channel.get_live_channel_inputs_ids import _get_live_channel_inputs_ids
from nomad_media_pip.admin.live_input.delete_live_input import _delete_live_input
from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _delete_live_channel(AUTH_TOKEN, URL, CHANNEL_ID, DELETE_INPUTS, DEBUG):
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}"

    # If delete Live Inputs then get their IDs
    INPUT_IDS = None
    if (DELETE_INPUTS == True):
        INPUT_IDS = _get_live_channel_inputs_ids(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG)


    # Create header for the request
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        'Content-Type': 'application/json'
    }

    try:
        # Send the request
        RESPONSE = requests.delete(API_URL, headers= HEADERS)

        # If the Live Channel had Live Inputs
        if (DELETE_INPUTS and INPUT_IDS and len(INPUT_IDS) > 0):
            print("Deleting Channel Inputs...")
            # Loop deleted Live Channel Live Inputs
            for ID in INPUT_IDS:
                # Delete Live Input
                _delete_live_input(AUTH_TOKEN, URL, ID, DEBUG)

        # Return JSON response
        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, f"Delete Live Channel {CHANNEL_ID} failed")

