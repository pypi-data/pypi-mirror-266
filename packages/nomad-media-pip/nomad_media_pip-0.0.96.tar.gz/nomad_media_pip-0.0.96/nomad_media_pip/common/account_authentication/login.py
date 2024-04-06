from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _login(URL, USERNAME, PASSWORD, DEBUG):
        
    API_URL = f"{URL}/api/account/login"

    # Create header for the request
    HEADERS = {
        'Content-Type': 'application/json'
    }

    # Build the payload BODY
    BODY = {
        "username": USERNAME,
        "password": PASSWORD
    }

    if DEBUG: print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))
    
        if not RESPONSE.ok:
            if RESPONSE.status_code == 409:
                return("Login info incorrect")
            raise Exception()
        

        return RESPONSE.json()
            

    except:
        _api_exception_handler(RESPONSE, "Login failed")

