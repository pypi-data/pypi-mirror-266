from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests
from urllib.parse import urlencode

def _get_asset_child_nodes(AUTH_TOKEN, URL, ID, FOLDER_ID, SORT_COLUMN, IS_DESC, PAGE_INDEX,
                           PAGE_SIZE, DEBUG):
    
    API_URL = f"{URL}/api/admin/asset/{ID}/getAssetChildNodes"

    PARAMS = {
        "folderId": FOLDER_ID,
        "sortColumn": SORT_COLUMN,
        "isDesc": IS_DESC,
        "pageIndex": PAGE_INDEX,
        "pageSize": PAGE_SIZE
    }

    API_URL = f"{API_URL}?{urlencode(PARAMS)}"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: GET")

    try:
        RESPONSE = requests.get(API_URL, headers=HEADERS)

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Get asset child nodes failed")

