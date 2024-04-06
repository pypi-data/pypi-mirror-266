from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_intelligent_schedule(AUTH_TOKEN, URL, DEFAULT_VIDEO_ASSET, NAME, THUMBNAIL_ASSET, 
                                 TIME_ZONE_ID, DEBUG):
    
    API_URL = f"{URL}/api/admin/schedule"

    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "defaultVideoAsset": DEFAULT_VIDEO_ASSET,
        "name": NAME,
        "scheduleType": "3",
        "thumbnailAsset": THUMBNAIL_ASSET,
        "timeZoneId": TIME_ZONE_ID
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Create Intelligent Schedule Failed")