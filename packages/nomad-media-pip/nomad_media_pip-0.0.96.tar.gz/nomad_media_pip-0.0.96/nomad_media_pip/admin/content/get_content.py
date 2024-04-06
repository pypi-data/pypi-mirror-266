from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_content(AUTH_TOKEN, URL, ID, CONTENT_DEFINITION_ID, IS_REVISION, DEBUG):
    API_URL = f"{URL}/api/content/{ID}?contentDefinitionId={CONTENT_DEFINITION_ID}"
    
    if IS_REVISION is not None:
        API_URL += f"&isRevision={IS_REVISION}"

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers=HEADERS)

        if (not RESPONSE.ok):
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, f"Getting content {ID} failed")