from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _start_workflow(AUTH_TOKEN, URL, ACTION_ARGUMENTS, TARGET_IDS, DEBUG):

    API_URL = f"{URL}/api/admin/asset/startWorkflow"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "actionArguments": ACTION_ARGUMENTS,
        "targetIds": TARGET_IDS
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Start workflow failed")