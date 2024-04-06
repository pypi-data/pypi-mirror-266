from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json, time

def _extend_live_schedule(AUTH_TOKEN, URL, EVENT_ID, RECURRING_DAYS, RECURRING_WEEKS,
                          END_DATE, DEBUG):
    
    API_URL = f"{URL}/api/admin/liveSchedule/content/{EVENT_ID}/copy"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "recurringDays": RECURRING_DAYS,
        "recurringWeeks": RECURRING_WEEKS,
        "endDate": END_DATE,
        "timeZoneOffsetSeconds": -time.timezone
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent= 4)})")

    try:
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
    except:
        _api_exception_handler(RESPONSE, "Extend Live Schedule Failed")