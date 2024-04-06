from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _add_custom_properties(AUTH_TOKEN, URL, ID, NAME, DATE, CUSTOM_PROPERTIES, DEBUG):

    API_URL = f"{URL}/api/admin/asset/{ID}"
        
    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    # Build the payload BODY
    BODY = {
        "displayName": NAME,
        "displayDate": DATE,
        "customProperties": CUSTOM_PROPERTIES
    }

    if DEBUG: 
        print(f"URL: {API_URL},\nMETHOD: PATCH,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.patch(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "add custom properties failed")

