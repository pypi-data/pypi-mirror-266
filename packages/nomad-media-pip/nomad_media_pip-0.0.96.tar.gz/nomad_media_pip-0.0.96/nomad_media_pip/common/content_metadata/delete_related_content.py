from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _delete_related_content(AUTH_TOKEN, URL, CONTENT_ID, RELATED_CONTENT_ID, CONTENT_DEFINITION, 
                            API_TYPE, DEBUG):

    API_URL = f"{URL}/api/admin/related/delete" if API_TYPE == "admin" else f"{URL}/api/content/related/delete"
        
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
                "relatedContentId": RELATED_CONTENT_ID
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
        _api_exception_handler(RESPONSE, "delete related content failed")

