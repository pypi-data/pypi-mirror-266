from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _get_video_tracking(AUTH_TOKEN, URL, ASSET_ID, TRACKING_EVENT, SECOND, DEBUG) :
    API_URL = f"{URL}/api/asset/tracking?assetId={ASSET_ID}"

    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if TRACKING_EVENT:
        apiUrl += f"&trackingEvent={TRACKING_EVENT}"
    

    if SECOND:
        apiUrl += f"&second={SECOND}"
    

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Get video tracking service failed")
    
