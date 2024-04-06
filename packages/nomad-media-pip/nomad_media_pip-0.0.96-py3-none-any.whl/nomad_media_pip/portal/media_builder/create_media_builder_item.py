from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_media_builder_item(AUTH_TOKEN, URL, ID, SOURCE_ASSET_ID, START_TIME_CODE,
                               END_TIME_CODE, SOURCE_ANNOATION_ID, RELATED_CONTENTS, DEBUG):
    
    API_URL = f"{URL}/api/mediaBuilder/{ID}/items"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "sourceAssetId": SOURCE_ASSET_ID,
        "startTimeCode": START_TIME_CODE,
        "endTimeCode": END_TIME_CODE,
        "sourceAnnotationId": SOURCE_ANNOATION_ID,
        "relatedContent": RELATED_CONTENTS
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Create Media Builder Item Failed")