from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _get_security_groups(AUTH_TOKEN, URL, DEBUG):
    API_URL = f"{URL}/api/lookup/22?lookupKey=99e8767a-00ba-4758-b9c2-e07b52c47016"

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if (DEBUG):
        print(f"API_URL: {API_URL}\nMETHOD: GET")

    try:
        # Send the request
        RESPONSE = requests.get(API_URL, headers= HEADERS)
        
        # If not found return None
        if (not RESPONSE.ok):
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, f"Get Security Groups failed")