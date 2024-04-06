from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _delete_saved_search(AUTH_TOKEN, URL, ID, DEBUG):

    API_URL = f"{URL}/api/portal/savedsearch/{ID}"

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: DELETE")

    try:
        RESPONSE = requests.delete(API_URL, headers=HEADERS)

        if not RESPONSE.ok:
            raise Exception()
    
    except:
        _api_exception_handler(RESPONSE, "Delete saved search failed")