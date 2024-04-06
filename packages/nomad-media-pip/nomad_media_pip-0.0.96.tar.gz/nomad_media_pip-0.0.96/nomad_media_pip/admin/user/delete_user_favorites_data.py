from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests

def _delete_user_favorites_data(AUTH_TOKEN, URL, USER_ID, DEBUG):

    API_URL = f"{URL}/api/admin/user/favorite/{USER_ID}"

    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: DELETE")

    try:
        RESPONSE = requests.delete(API_URL, headers= HEADERS)
        
        if not RESPONSE.ok:
            raise Exception()
    except:
        _api_exception_handler(RESPONSE, "Delete User Favorites Data Failed")