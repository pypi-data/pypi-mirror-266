from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _download_archive_asset(AUTH_TOKEN, URL, API_TYPE, ASSET_IDS, FILE_NAME, DOWNLOAD_PROXY,
                            DEBUG):
    
    API_URL = f"{URL}/api/admin/asset/download-archive" if API_TYPE == "admin" else f"{URL}/api/asset/download-archive"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "assetIds": ASSET_IDS
    }

    if API_TYPE == "admin":
        BODY["fileName"] = FILE_NAME
        BODY["downloadProxy"] = DOWNLOAD_PROXY

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Download archive asset failed")