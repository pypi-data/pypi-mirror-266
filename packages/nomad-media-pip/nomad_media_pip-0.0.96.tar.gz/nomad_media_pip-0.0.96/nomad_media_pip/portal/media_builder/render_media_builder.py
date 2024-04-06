from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _render_media_builder(AUTH_TOKEN, URL, ID, DEBUG):

    API_URL = f"{URL}/api/mediaBuilder/{ID}/render"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Render Media Builder Failed")