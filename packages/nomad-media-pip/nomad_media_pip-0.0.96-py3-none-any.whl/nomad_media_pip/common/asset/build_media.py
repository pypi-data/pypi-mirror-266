from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _build_media(AUTH_TOKEN, URL, SOURCE, TITLE, TAGS, COLLECTIONS, RELATED_CONTENT,
                 DESTINATION_FOLDER_ID, VIDEO_BITRATE, AUDIO_TRACKS, DEBUG):
    
    API_URL = f"{URL}/api/asset/build-media"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "source": SOURCE,
        "title": TITLE,
        "destinationFolderId": DESTINATION_FOLDER_ID,
        "tags": TAGS,
        "collections": COLLECTIONS,
        "relatedContent": RELATED_CONTENT,
        "videoBitrate": VIDEO_BITRATE,
        "audioTracks": AUDIO_TRACKS
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Build media failed")