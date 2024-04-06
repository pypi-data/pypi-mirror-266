from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _patch_saved_search(AUTH_TOKEN, URL, ID, NAME, FEATURED, BOOKMARKED, PUBLIC, SEQUENCE, 
                        DEBUG):

    API_URL = f"{URL}/api/portal/savedsearch/{ID}"

    BODY = {
        key: value for key, value in {
            "name": NAME,
            "featured": FEATURED,
            "bookmarked": BOOKMARKED,
            "public": PUBLIC,
            "sequence": SEQUENCE
        }.items() if value is not None
    }

    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: PATCH\nBODY:\n{json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.patch(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Patch saved search failed")