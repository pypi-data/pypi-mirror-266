from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _create_form(AUTH_TOKEN, URL, CONTENT_DEFINITION_ID, FORM_INFO, DEBUG):

    API_URL = f"{URL}/api/media/form/{CONTENT_DEFINITION_ID}"
        
    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer "+ AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    # Build the payload BODY
    BODY = FORM_INFO

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Forms failed")

