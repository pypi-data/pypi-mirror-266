from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_playlist_video(AUTH_TOKEN, URL, PLAYLIST_ID, ASSET, PREVIOUS_ITEM, DEBUG):
    
    API_URL = f"{URL}/api/admin/schedule/{PLAYLIST_ID}/item"
    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    
    BODY = {
        "asset": ASSET,
        "previousItem": PREVIOUS_ITEM
    }
    
    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")
    
    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Create Playlist Video Failed")