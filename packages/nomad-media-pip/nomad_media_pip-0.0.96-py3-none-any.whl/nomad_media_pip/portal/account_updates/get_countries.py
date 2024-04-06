from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, re, requests

def _get_countries(AUTH_TOKEN, URL, DEBUG):

    if (not AUTH_TOKEN):
        raise Exception("Authentication Token: The authentication token is invalid")
  
    EDITED_URL = re.sub(r'https://(.+?)\.', 'https://', URL)
    EDITED_URL = EDITED_URL[:EDITED_URL.rfind('/')]
    API_URL = f"{EDITED_URL}/config/ea1d7060-6291-46b8-9468-135e7b94021b/lookups.json"
  
    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG: 
        print(f"URL: {API_URL}\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers=HEADERS)
        if not RESPONSE.ok:
            raise Exception()

        INFO = RESPONSE.json()
        return INFO[5]["children"]
    except:
        _api_exception_handler(RESPONSE, "Get countries failed")