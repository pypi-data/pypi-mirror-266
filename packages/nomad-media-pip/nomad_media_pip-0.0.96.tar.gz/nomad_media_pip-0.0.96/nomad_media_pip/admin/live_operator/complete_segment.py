from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _complete_segment(AUTH_TOKEN, URL, ID, RELATED_CONTENT_IDS, TAG_IDS, DEBUG):
    API_URL = f"{URL}/api/admin/liveOperator/{ID}/completeSegment"

    HEADERS = {
        "Authorization": "Bearer " +  AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "liveOperatorId": ID,
    }

    if RELATED_CONTENT_IDS and isinstance(RELATED_CONTENT_IDS, list) and len(RELATED_CONTENT_IDS) > 0:
        BODY["relatedContent"] = [{"id": id} for id in RELATED_CONTENT_IDS]
    
    if TAG_IDS and isinstance(TAG_IDS, list) and len(TAG_IDS) > 0:
        BODY["tags"] = [{"id": id} for id in RELATED_CONTENT_IDS]

    if (DEBUG):
        print(f"API_URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent= 4)}")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        # If not found return None
        if (not RESPONSE.ok):
            raise Exception()
    
    except:
        _api_exception_handler(RESPONSE, f"Completing segment for Live Channel {ID} failed")