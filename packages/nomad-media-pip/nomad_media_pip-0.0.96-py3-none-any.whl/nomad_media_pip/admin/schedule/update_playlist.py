from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.schedule.get_playlist import _get_playlist

import requests, json

def _update_playlist(AUTH_TOKEN, URL, ID, DEFAULT_VIDEO_ASSET, LOOP_PLAYLIST, NAME,
                     THUMBNAIL_ASSET, DEBUG):
        
        API_URL = f"{URL}/api/admin/schedule/{ID}"
        
        PLAYLIST = _get_playlist(AUTH_TOKEN, URL, ID, DEBUG)
        
        HEADERS = {
            "Authorization": "Bearer " + AUTH_TOKEN,
            "Content-Type": "application/json"
        }
    
        BODY = {
            "defaultVideoAsset": DEFAULT_VIDEO_ASSET or PLAYLIST.get("defaultVideoAsset"),
            "id": ID,
            "loopPlaylist": LOOP_PLAYLIST or PLAYLIST.get("loopPlaylist"),
            "name": NAME or PLAYLIST.get("name"),
            "scheduleType": "1",
            "thumbnailAsset": THUMBNAIL_ASSET or PLAYLIST.get("thumbnailAsset")
        }
    
        if DEBUG:
            print(f"URL: {API_URL},\nMETHOD: PUT,\nBODY: {json.dumps(BODY, indent=4)}")
    
        try:
            RESPONSE = requests.put(API_URL, headers= HEADERS, data= json.dumps(BODY))
            
            if not RESPONSE.ok:
                raise Exception()
            
            return RESPONSE.json()
        except:
            _api_exception_handler(RESPONSE, "Update Playlist Failed")