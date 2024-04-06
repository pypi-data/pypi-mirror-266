from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_playlist(AUTH_TOKEN, URL, NAME, THUMBNAIL_ASSET, LOOP_PLAYLIST, DEFAULT_VIDEO_ASSET, DEBUG):

    API_URL = f"{URL}/api/admin/schedule"
    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    
    BODY = {
        "name": NAME,
        "scheduleType": "1",
        "thumbnailAsset": THUMBNAIL_ASSET,
        "loopPlaylist": LOOP_PLAYLIST,
        "defaultVideoAsset": DEFAULT_VIDEO_ASSET
    }
    
    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")
    
    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Create Playlist Failed")