from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _next_event(AUTH_TOKEN, URL, CHANNEL_ID, DEBUG):
    
    API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/nextEvent"
    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    
    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")
    
    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS)
        
        if not RESPONSE.ok:
            raise Exception()
    except:
        _api_exception_handler(RESPONSE, "Get Next Event Failed")