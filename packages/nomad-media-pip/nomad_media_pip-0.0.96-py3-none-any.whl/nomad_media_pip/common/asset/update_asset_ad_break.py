from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.common.asset.get_asset_ad_breaks import _get_asset_ad_breaks

import requests, json

def _update_asset_ad_break(AUTH_TOKEN, URL, ASSET_ID, AD_BREAK_ID, TIME_CODE, TAGS, LABELS,
                           DEBUG):

    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/adbreak/{AD_BREAK_ID}"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    ASSET_AD_BREAKS = _get_asset_ad_breaks(AUTH_TOKEN, URL, ASSET_ID, DEBUG)
    AD_BREAK = next((ad_break for ad_break in ASSET_AD_BREAKS if ad_break["id"] == AD_BREAK_ID), None)

    BODY = {
        "id": AD_BREAK_ID,
        "timecode": TIME_CODE or AD_BREAK.get("timecode"),
        "tags": TAGS or AD_BREAK.get("tags"),
        "labels": LABELS or AD_BREAK.get("labels")
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: PUT\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.put(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Update ad break failed") 