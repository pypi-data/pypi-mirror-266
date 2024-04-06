from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests
from urllib.parse import urlencode

def _records_asset_tracking_beacon(AUTH_TOKEN, URL, ASSET_ID, TRACKING_EVENT, LIVE_CHANNEL_ID,
                                  CONTENT_ID, SECOND, DEBUG):
    
    API_URL = f"{URL}/api/asset/tracking"

    PARAMS = {
        "trackingEvent": TRACKING_EVENT,
        "assetId": ASSET_ID,
        "liveChannelId": LIVE_CHANNEL_ID,
        "contentId": CONTENT_ID,
        "second": SECOND
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
    
    except:
        _api_exception_handler(RESPONSE, "Record asset tracking beacon failed")