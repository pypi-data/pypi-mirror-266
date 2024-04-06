from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _move_media_builder_item(AUTH_TOKEN, URL, ID, ITEM_ID, PREVIOUS_ITEM_ID, DEBUG):

    API_URL = f"{URL}/api/mediaBuilder/{ID}/items/{ITEM_ID}/move"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "previousItemId": PREVIOUS_ITEM_ID
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

    except:
        _api_exception_handler(RESPONSE, "Move Media Builder Item Failed")