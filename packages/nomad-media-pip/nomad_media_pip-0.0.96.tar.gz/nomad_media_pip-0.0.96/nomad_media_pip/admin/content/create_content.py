from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _create_content(AUTH_TOKEN, URL, CONTENT_DEFINITION_ID, LANGUAGE_ID, DEBUG):
  
    API_URL = f"{URL}/api/content/new?contentDefinitionId={CONTENT_DEFINITION_ID}"
  
    if LANGUAGE_ID: API_URL += f"&language={LANGUAGE_ID}"

    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers=HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
        ID = json.loads(RESPONSE.text)
        return ID
        
        
    except:
        _api_exception_handler(RESPONSE, "Get content id failed: ")
    
