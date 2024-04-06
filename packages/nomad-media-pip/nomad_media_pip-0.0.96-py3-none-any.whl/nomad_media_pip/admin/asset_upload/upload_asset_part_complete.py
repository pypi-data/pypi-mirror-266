from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _upload_asset_part_complete(AUTH_TOKEN, URL, PART_ID, ETAG, DEBUG):

    API_URL = f"{URL}/api/asset/upload/part/" + PART_ID + "/complete"
        
    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    # Build the payload BODY
    BODY = {
        "etag": ETAG
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

    except:
        _api_exception_handler(RESPONSE, "Upload asset part failed")

