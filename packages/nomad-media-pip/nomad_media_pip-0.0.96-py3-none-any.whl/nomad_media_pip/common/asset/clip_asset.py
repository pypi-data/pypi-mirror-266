from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _clip_asset(AUTH_TOKEN, URL, ASSET_ID, ASSET_TYPE, START_TIME_CODE, END_TIME_CODE, 
                TITLE, OUTPUT_FOLDER_ID, TAGS, COLLECTIONS, RELATED_CONTENTS, VIDEO_BITRATE, 
                AUDIO_TRACKS, DEBUG):
    
    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/clip" if ASSET_TYPE == "admin" else f"{URL}/api/asset/{ASSET_ID}/clip"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "startTimecode": START_TIME_CODE,
        "endTimecode": END_TIME_CODE,
        "title": TITLE,
        "outputFolderId": OUTPUT_FOLDER_ID,
        "tags": TAGS,
        "collections": COLLECTIONS,
        "relatedContent": RELATED_CONTENTS,
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
        _api_exception_handler(RESPONSE, "Clip asset failed")