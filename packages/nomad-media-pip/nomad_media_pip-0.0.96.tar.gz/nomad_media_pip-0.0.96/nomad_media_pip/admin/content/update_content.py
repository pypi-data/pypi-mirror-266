from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.content.get_content import _get_content

import json, requests

def _update_content(AUTH_TOKEN, URL, ID, CONTENT_DEFINITION_ID, PROPERTIES, 
                    LANGUAGE_ID, DEBUG):
    # Create header for the request
    if not AUTH_TOKEN:
        raise Exception("Authorization token not found")
  
    API_URL = f"{URL}/api/content/{ID}"
    
    HEADERS = {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + AUTH_TOKEN
    }

    try:
        CONTENT_INFO = _get_content(AUTH_TOKEN, URL, ID, CONTENT_DEFINITION_ID, DEBUG)
    except:
        CONTENT_INFO = None

    # Build the payload body
    BODY = {
        "contentDefinitionId": CONTENT_DEFINITION_ID or (CONTENT_INFO and CONTENT_INFO["contentDefinitionId"]),
        "contentId": ID or (CONTENT_INFO and CONTENT_INFO["contentId"]),
        "languageId": LANGUAGE_ID or (CONTENT_INFO and CONTENT_INFO["languageId"]),
    }           

    if CONTENT_INFO:
        BODY["properties"] = {PROPERTY: PROPERTIES.get(PROPERTY, PROPERTY) for PROPERTY in CONTENT_INFO["properties"]}
    else:
        BODY["properties"] = PROPERTIES

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send POST request
        RESPONSE = requests.put(API_URL, headers=HEADERS, data=json.dumps(BODY))

        # Check for success
        if (not RESPONSE.ok):
            raise Exception()
        
        # Get the response
        ID = RESPONSE.json()

        # Return the ID
        return ID
    
    except:
        _api_exception_handler(RESPONSE, "Create/Update movie failed")

