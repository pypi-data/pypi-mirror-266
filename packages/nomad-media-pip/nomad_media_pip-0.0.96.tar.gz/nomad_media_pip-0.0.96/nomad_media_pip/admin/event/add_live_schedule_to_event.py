from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _add_live_schedule_to_event(AUTH_TOKEN, URL, EVENT_ID, SLATE_VIDEO, PREROLL_VIDEO,
                                POSTROLL_VIDEO, IS_SECURE_OUTPUT, ARCHIVE_FOLDER_ASSET,
                                PRIMARY_LIVE_INPUT, BACKUP_LIVE_INPUT, 
                                PRIMARY_LIVESTREAM_INPUT_URL, BACKUP_LIVESTREAM_INPUT_URL, 
                                EXTERNAL_OUTPUT_PROFILES, DEBUG):
    
    API_URL = f"{URL}/api/admin/liveSchedule"
    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }
    
    BODY = {
        "contentId": EVENT_ID,
        "slateVideo": SLATE_VIDEO,
        "prerollVideo": PREROLL_VIDEO,
        "postrollVideo": POSTROLL_VIDEO,
        "isSecureOutput": IS_SECURE_OUTPUT,
        "archiveFolderAsset": ARCHIVE_FOLDER_ASSET,
        "primaryLiveInput": PRIMARY_LIVE_INPUT,
        "backupLiveInput": BACKUP_LIVE_INPUT,
        "primaryLivestreamInputUrl": PRIMARY_LIVESTREAM_INPUT_URL,
        "backupLivestreamInputUrl": BACKUP_LIVESTREAM_INPUT_URL,
        "externalOutputProfiles": EXTERNAL_OUTPUT_PROFILES
    }
    
    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent= 4)})")
    
    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
        
        if not RESPONSE.ok:
            raise Exception()
    except:
        _api_exception_handler(RESPONSE, "Add Live Schedule To Event Failed")
