from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests
from urllib.parse import urlencode

def _clear_continue_watching(AUTH_TOKEN, URL, USER_ID, ASSET_ID, DEBUG):

    API_URL = f"{URL}/api/media/clear-watching?userId={USER_ID}"

    if ASSET_ID:
        API_URL +=  f"&assetId={ASSET_ID}"

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN 
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS)
        if not RESPONSE.ok:
            raise Exception()
    
    except:
        _api_exception_handler(RESPONSE, "Clear Continue Watching Failed")      