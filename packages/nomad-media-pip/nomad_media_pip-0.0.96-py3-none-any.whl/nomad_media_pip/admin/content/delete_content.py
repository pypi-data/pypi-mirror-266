from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _delete_content(AUTH_TOKEN, URL, ID, CONTENT_DEFINITION_ID, DEBUG):
  
    API_URL = f"{URL}/api/content/{ID}?contentDefinitionId={CONTENT_DEFINITION_ID}"
    
    HEADERS = {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: DELETE")

    try:
        RESPONSE = requests.delete(API_URL, headers=HEADERS)

        if (RESPONSE.ok):
            return True
        
        raise Exception()

    except:
        _api_exception_handler(RESPONSE, "Deleting content failed")