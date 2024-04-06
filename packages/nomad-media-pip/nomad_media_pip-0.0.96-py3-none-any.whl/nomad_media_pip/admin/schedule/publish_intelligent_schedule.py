from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _publish_intelligent_schedule(AUTH_TOKEN, URL, SCHEDULE_ID, NUMBER_OR_LOCKED_DAYS, DEBUG):

    API_URL = f"{URL}/api/admin/schedule/{SCHEDULE_ID}/publish"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "number_of_days": NUMBER_OR_LOCKED_DAYS
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Publish Intelligent Schedule Failed")