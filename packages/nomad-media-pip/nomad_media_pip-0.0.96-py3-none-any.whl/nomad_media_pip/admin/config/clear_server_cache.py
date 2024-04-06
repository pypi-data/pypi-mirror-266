from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _clear_server_cache(AUTH_TOKEN, URL, DEBUG):
    API_URL = f"{URL}/api/config/clearServerCache"

    # Create header for the request
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()
    
    except:
        _api_exception_handler(RESPONSE, "Clear server cache failed")