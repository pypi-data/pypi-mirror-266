from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_tag_or_collection(AUTH_TOKEN, URL, TYPE, TAG_NAME, DEBUG):
    
    API_URL = f"{URL}/api/admin/{TYPE}"
    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    
    BODY = {
        "name": TAG_NAME
    }
    
    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent= 4)}")
    
    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Create Tag or Collection Failed")