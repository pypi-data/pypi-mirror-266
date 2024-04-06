from nomad_media_pip.portal.account_updates.get_user import _get_user
from nomad_media_pip.portal.account_updates.get_countries import _get_countries
from nomad_media_pip.portal.account_updates.get_states import _get_states
from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _update_user(AUTH_TOKEN, URL, ADDRESS, ADDRESS2, CITY, FIRST_NAME, LAST_NAME, 
        PHONE_NUMBER, PHONE_EXT, POSTAL_CODE, ORGANIZATION, COUNTRY, STATE, DEBUG):
  
    USER_INFO = _get_user(AUTH_TOKEN, URL, DEBUG)

    API_URL = f"{URL}/api/account/user"
  
    # Create header for the request
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    STATE_SELECTED = next((state for state in _get_states(AUTH_TOKEN, URL, DEBUG) if state["label"] == STATE), None)
    COUNTRY_SELECTED = next((country for country in _get_countries(AUTH_TOKEN, URL, DEBUG) if country["label"] == COUNTRY), None)

    BODY = {
        key: value if value is not None else USER_INFO.get(key)
        for key, value in {
            "address": ADDRESS,
            "address2": ADDRESS2,
            "city": CITY,
            "stateId": STATE_SELECTED,
            "country": COUNTRY_SELECTED,
            "firstName": FIRST_NAME,
            "lastName": LAST_NAME,
            "phone": PHONE_NUMBER,
            "phoneExt": PHONE_EXT,
            "postalCode": POSTAL_CODE,
            "organization": ORGANIZATION,
        }.items()
    }



    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: PUT\nBODY: {json.dumps(BODY, indent=4)}")
    
    try:
        RESPONSE = requests.put(API_URL, headers=HEADERS, data=json.dumps(BODY))
        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()
    except:
        _api_exception_handler(RESPONSE, "Update user failed")