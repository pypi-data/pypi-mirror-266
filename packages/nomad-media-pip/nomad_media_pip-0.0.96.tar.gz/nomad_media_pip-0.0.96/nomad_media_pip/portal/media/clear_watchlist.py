from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _clear_watchlist(AUTH_TOKEN, URL, USER_ID, DEBUG):

    API_URL = f"{URL}/api/media/clear-watching?userId={USER_ID}"

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
        _api_exception_handler(RESPONSE, "Clear Watchlist Failed")