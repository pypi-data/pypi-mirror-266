from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _delete_media_builder(AUTH_TOKEN, URL, ID, DEBUG):

    API_URL = f"{URL}/api/mediaBuilder/{ID}"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: DELETE")

    try:
        RESPONSE = requests.delete(API_URL, headers=HEADERS)

        if not RESPONSE.ok:
            raise Exception()

    except:
        _api_exception_handler(RESPONSE, "Delete Media Builder Failed")