from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

# @param {string} AUTH_TOKEN - The authentication token

def _register_guest(AUTH_TOKEN, URL, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, DEBUG):
  
    API_URL = f"{URL}/api/account/register-guest"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }
    
    # replace username and password with your username and password
    BODY = {
      	"email": EMAIL,
        "firstName": FIRST_NAME,
        "lastName": LAST_NAME,
        "password": PASSWORD
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
      	_api_exception_handler(RESPONSE, "Registering guest failed")

