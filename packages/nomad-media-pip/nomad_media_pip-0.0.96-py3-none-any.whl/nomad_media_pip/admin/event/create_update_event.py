from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_and_update_event(AUTH_TOKEN, URL, CONTENT_ID, CONTENT_DEFINITION_ID, 
                             NAME, START_DATETIME, END_DATETIME, EVENT_TYPE, SERIES,
                             DISABLED, OVERRIED_SERIES_PROPERTIES, SERIES_PROPERTIES, DEBUG):
    
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if (CONTENT_ID == "" or CONTENT_ID == None):
        API_URL = f"{URL}/api/content/new?contentDefinitionId={CONTENT_DEFINITION_ID}"

        if DEBUG:
            print(f"URL: {API_URL},\nMETHOD: GET")

        try:
            RESPONSE = requests.get(API_URL, headers= HEADERS)

            if not RESPONSE.ok:
                raise Exception()

            INFO = RESPONSE.json()
            CONTENT_ID = INFO["contentId"]
        except:
            _api_exception_handler(RESPONSE, "Create Event Failed")

    API_URL = f"{URL}/api/content/{CONTENT_ID}"

    if not SERIES_PROPERTIES or not OVERRIED_SERIES_PROPERTIES: SERIES_PROPERTIES = {}

    SERIES_PROPERTIES["name"] = NAME if NAME else SERIES["description"]
    SERIES_PROPERTIES["startDateTime"] = START_DATETIME
    SERIES_PROPERTIES["endDateTime"] = END_DATETIME
    SERIES_PROPERTIES["eventType"] = EVENT_TYPE
    if SERIES: SERIES_PROPERTIES["series"] = SERIES
    SERIES_PROPERTIES["disabled"] = DISABLED
    SERIES_PROPERTIES["overrideSeriesDetails"] = OVERRIED_SERIES_PROPERTIES

    BODY = {
        "contentId": CONTENT_ID,
        "contentDefinitionId": CONTENT_DEFINITION_ID,
        "properties": SERIES_PROPERTIES
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: PUT,\nBODY: {json.dumps(BODY, indent= 4)})")

    try:
        RESPONSE = requests.put(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Create Event Failed")