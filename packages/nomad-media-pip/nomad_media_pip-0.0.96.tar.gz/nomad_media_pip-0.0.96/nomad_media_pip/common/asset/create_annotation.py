from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_annotation(AUTH_TOKEN, URL, ASSET_ID, START_TIME_CODE, END_TIME_CODE, FIRST_KEYWORD,
                       SECOND_KEYWORD, DESCRIPTION, COUNTRY, CONTENT_ID, IMAGE_URL, DEBUG):
    
    API_URL = f"{URL}/api/asset/{ASSET_ID}/annotation"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "startTimecode": START_TIME_CODE,
        "endTimecode": END_TIME_CODE,
        "properties": {
            "firstKeyword": FIRST_KEYWORD,
            "secondKeyword": SECOND_KEYWORD,
            "description": DESCRIPTION,
            "country": COUNTRY
        },
        "contentId": CONTENT_ID,
        "imageUrl": IMAGE_URL
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Create annotation failed")