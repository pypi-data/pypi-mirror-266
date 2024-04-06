from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _add_tag_or_collection(AUTH_TOKEN, URL, TYPE, CONTENT_ID, CONTENT_DEFINITION, NAME, 
                           TAG_ID, CREATE_NEW, API_TYPE, DEBUG):

    API_URL = f"{URL}/api/admin/{TYPE}/content" if API_TYPE == "admin" else f"{URL}/api/content/{TYPE}"
        
    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    # Build the payload BODY
    BODY = {
        "items": [
            {
                "contentDefinition": CONTENT_DEFINITION,
                "contentId": CONTENT_ID,
                "name": NAME,
                "createNew": CREATE_NEW,
                f"{TYPE}Id": TAG_ID
            }
        ]
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "add tag or collection failed")

