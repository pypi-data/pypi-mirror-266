from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _start_segment(AUTH_TOKEN, URL, ID, DEBUG):
    API_URL = f"{URL}/api/admin/liveOperator/{ID}/startSegment"

    HEADERS = {
        "Authorization": "Bearer " +  AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if (DEBUG):
        print(f"API_URL: {API_URL}\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS)

        # If not found return None
        if (not RESPONSE.ok):
            raise Exception()
        
    except:
        _api_exception_handler(RESPONSE, f"Starting segment for Live Channel {ID} failed")