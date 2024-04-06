from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

'''
 * Refresh Token
 *
 * @param {string} REFRESH_TOKEN | The refresh token
 *
 * @returns {string} Authentication token
'''
def _refresh_token(AUTH_TOKEN, URL, REFRESH_TOKEN, DEBUG):
    API_URL = f"{URL}/api/account/refresh-token"

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json',
        'Authorization': f"Bearer {AUTH_TOKEN}"
    }

    # Build the payload BODY
    BODY = {
        "refreshToken": REFRESH_TOKEN
    }

    if DEBUG:
        print(f"API URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Refresh Token failed")

