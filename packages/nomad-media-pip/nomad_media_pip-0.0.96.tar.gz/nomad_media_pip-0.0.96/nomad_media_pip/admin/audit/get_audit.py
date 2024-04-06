from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _get_audit(AUTH_TOKEN, URL, ID, DEBUG):
    API_URL = f"{URL}/api/admin/audit/{ID}"

    # Create header for the request
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: GET")

    try:
        # Send the request
        RESPONSE = requests.get(API_URL, headers= HEADERS)

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Get audit failed")