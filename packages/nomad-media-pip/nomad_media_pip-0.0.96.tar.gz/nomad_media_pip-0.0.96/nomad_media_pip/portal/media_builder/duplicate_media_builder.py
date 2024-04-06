from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _duplicate_media_builder(AUTH_TOKEN, URL, ID, NAME, DESTINATION_FOLDER_ID, COLLECTIONS,
                             RELATED_CONTENTS, PROPERTIES, DEBUG):
    
    API_URL = f"{URL}/api/mediaBuilder/{ID}/duplicate"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "name": NAME,
        "destinationFolderId": DESTINATION_FOLDER_ID,
        "collections": COLLECTIONS,
        "relatedContent": RELATED_CONTENTS,
        "properties": PROPERTIES
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Duplicate Media Builder Failed")