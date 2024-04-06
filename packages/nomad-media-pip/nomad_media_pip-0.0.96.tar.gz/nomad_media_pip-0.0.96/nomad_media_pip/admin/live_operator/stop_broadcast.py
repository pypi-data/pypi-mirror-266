from nomad_media_pip.admin.live_operator.wait_for_live_operator_status import _wait_for_live_operator_status
from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _stop_broadcast(AUTH_TOKEN, URL, ID, DEBUG):
    API_URL = f"{URL}/api/admin/liveOperator/{ID}/stop"

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
        
        _wait_for_live_operator_status(AUTH_TOKEN, URL, ID, "Idle", 1200, 20, DEBUG)
    
    except:
        _api_exception_handler(RESPONSE, f"Stopping broadcast for Live Channel {ID} failed")