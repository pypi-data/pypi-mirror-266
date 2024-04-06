from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

# @param {string} AUTH_TOKEN - The authentication token

def _remove_guest(AUTH_TOKEN, URL, CONTENT_ID, CONTENT_DEFINITION_ID, USER_ID,
                  EMAILS, CONTENT_SECURITY_ATTRIBUTE, DEBUG):
        
    API_URL = f"{URL}/api/account/remove-user"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }
    
    # replace username and password with your username and password
    BODY = {
      	"contentId": CONTENT_ID,
      	"contentDefinitionId": CONTENT_DEFINITION_ID,
        "userId": USER_ID,
        "emails": EMAILS,
        "contentSecurityAttribute": CONTENT_SECURITY_ATTRIBUTE
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
      	_api_exception_handler(RESPONSE, "Removing Guest Failed")

