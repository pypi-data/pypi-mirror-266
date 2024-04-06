from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.live_output_profile.get_live_output_profile import _get_live_output_profile

import requests, json

def _update_live_output_profile(AUTH_TOKEN, URL, ID, NAME, OUTPUT_TYPE, ENABLED, AUDIO_BITRATE,
                        OUTPUT_STREAM_KEY, OUTPUT_URL, SECONDARY_OUTPUT_STREAM_KEY,
                        SECONDARY_OUTPUT_URL, VIDEO_BITRATE, VIDEO_BITRATE_MODE,
                        VIDEO_CODEC, VIDEO_FRAMES_PER_SECOND, VIDEO_HEIGHT, VIDEO_WIDTH,
                        DEBUG):

    API_URL = f"{URL}/api/liveOutputProfile"

    HEADERS = {
        'Content-Type': 'application/json',
        "Authorization": "Bearer " + AUTH_TOKEN
    }

    PROFILE_INFO = _get_live_output_profile(AUTH_TOKEN, URL, ID, DEBUG)

    BODY = {
        "id": ID,
        "name": NAME or PROFILE_INFO.get("name"),
        "outputType": OUTPUT_TYPE or PROFILE_INFO.get("outputType"),
        "enabled": ENABLED or PROFILE_INFO.get("enabled"),
        "audioBitrate": AUDIO_BITRATE or PROFILE_INFO.get("audioBitrate"),
        "outputStreamKey": OUTPUT_STREAM_KEY or PROFILE_INFO.get("outputStreamKey"),
        "outputUrl": OUTPUT_URL or PROFILE_INFO.get("outputUrl"),
        "secondaryOutputStreamKey": SECONDARY_OUTPUT_STREAM_KEY or PROFILE_INFO.get("secondaryOutputStreamKey"),
        "secondaryOutputUrl": SECONDARY_OUTPUT_URL or PROFILE_INFO.get("secondaryOutputUrl"),
        "videoBitrate": VIDEO_BITRATE or PROFILE_INFO.get("videoBitrate"),
        "videoBitrateMode": VIDEO_BITRATE_MODE or PROFILE_INFO.get("videoBitrateMode"),
        "videoCodec": VIDEO_CODEC or PROFILE_INFO.get("videoCodec"),
        "videoFramesPerSecond": VIDEO_FRAMES_PER_SECOND or PROFILE_INFO.get("videoFramesPerSecond"),
        "videoHeight": VIDEO_HEIGHT or PROFILE_INFO.get("videoHeight"),
        "videoWidth": VIDEO_WIDTH or PROFILE_INFO.get("videoWidth")
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: PUT,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.put(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Update Live Output Profile Failed")