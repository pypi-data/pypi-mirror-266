from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _clip_live_channel(AUTH_TOKEN, URL, CHANNEL_ID, START_TIME_CODE, END_TIME_CODE, TITLE, 
                       OUTPUT_FOLDER_ID, TAGS, COLLECTIONS, RELATED_CONTENTS, VIDEO_BITRATE, 
                       AUDIO_TRACKS, DEBUG):
        
        API_URL = f"{URL}/api/liveChannel/{CHANNEL_ID}/clip"
        
        HEADERS = {
            "Authorization": "Bearer " + AUTH_TOKEN,
            "Content-Type": "application/json"
        }
        
        BODY = {
            "startTimeCode": START_TIME_CODE,
            "endTimeCode": END_TIME_CODE,
            "title": TITLE,
            "outputFolderId": OUTPUT_FOLDER_ID,
            "tags": TAGS,
            "collections": COLLECTIONS,
            "relatedContent": RELATED_CONTENTS,
            "videoBitrate": VIDEO_BITRATE,
            "audioTracks": AUDIO_TRACKS
        }
        
        if DEBUG:
            print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent= 4)}")
        
        try:
            RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
            
            if not RESPONSE.ok:
                raise Exception()
        except:
            _api_exception_handler(RESPONSE, "Clip Live Channel Failed")
        
        return RESPONSE.json()