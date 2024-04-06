from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.helpers.slugify import _slugify
from nomad_media_pip.admin.live_input.live_input_types import _LIVE_INPUT_TYPES
from nomad_media_pip.admin.live_input.live_input_statuses import _LIVE_INPUT_STATUSES
from nomad_media_pip.admin.live_input.wait_for_live_input_status import _wait_for_live_input_status

import json, requests

def _create_live_input(AUTH_TOKEN, URL, NAME, SOURCE, TYPE, IS_STANDARD, VIDEO_ASSET_ID, 
                       DESTINATIONS, SOURCES, DEBUG):
    API_URL = f"{URL}/api/liveInput"

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    # Build the payload BODY
    # Error Object of type set is not JSON serializable
    BODY = {
        "name": NAME,
        "internalName": _slugify(NAME),
        "type": { 
            "id": _LIVE_INPUT_TYPES[TYPE],
            "description": TYPE
        }
    }

    # Set the appropriate fields based on the type
    if (TYPE == "RTMP_PUSH"):
        if SOURCE: BODY["sourceCidr"] = SOURCE
    elif (TYPE == "RTMP_PULL" or TYPE == "RTP_PUSH" or TYPE == "URL_PULL"):
        if SOURCE: BODY["sources"] = [{ "url": SOURCE }]

    if IS_STANDARD: BODY["isStandard"] = IS_STANDARD
    if VIDEO_ASSET_ID: BODY["videoAsset"] = { "id": VIDEO_ASSET_ID }
    if DESTINATIONS: BODY["destinations"] = DESTINATIONS
    if SOURCES: BODY["sources"] = SOURCES

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL,  headers= HEADERS, data= json.dumps(BODY))
    
        # Parse JSON response
        INFO = RESPONSE.json()

        # Wait for the Live Input to be detached if it was just created
        _wait_for_live_input_status(AUTH_TOKEN, URL, INFO["id"], _LIVE_INPUT_STATUSES["Detached"], 15, 1)

        return INFO
    
    except:
        _api_exception_handler(RESPONSE, f"Creating Live Input {NAME} failed")

