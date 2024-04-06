from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.admin.live_output_profile_group.get_live_output_profile_group import _get_live_output_profile_group

import requests, json

def _update_live_output_profile_group(AUTH_TOKEN, URL, LIVE_OUTPUT_PROFILE_GROUP_ID, NAME, IS_ENABLED, MANIFEST_TYPE, IS_DEFAULT_GROUP, LIVE_OUTPUT_TYPE, ARCHIVE_LIVE_OUTPUT_PROFILE, LIVE_OUTPUT_PROFILES, DEBUG):

	API_URL = f"{URL}/api/liveOutputProfileGroup"

	HEADERS = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {AUTH_TOKEN}"
	}

	PROFILE_GROUP_INFO = _get_live_output_profile_group(AUTH_TOKEN, URL, LIVE_OUTPUT_PROFILE_GROUP_ID, DEBUG)

	BODY = {
		"id": LIVE_OUTPUT_PROFILE_GROUP_ID or PROFILE_GROUP_INFO.get("id"),
		"name": NAME or PROFILE_GROUP_INFO.get("name"),
		"isEnabled": IS_ENABLED or PROFILE_GROUP_INFO.get("isEnabled"),
		"manifestType": MANIFEST_TYPE or PROFILE_GROUP_INFO.get("manifestType"),
		"isDefaultGroup": IS_DEFAULT_GROUP or PROFILE_GROUP_INFO.get("isDefaultGroup"),
		"outputType": LIVE_OUTPUT_TYPE or PROFILE_GROUP_INFO.get("outputType"),
		"archiveOutputProfile": ARCHIVE_LIVE_OUTPUT_PROFILE or PROFILE_GROUP_INFO.get("archiveOutputProfile"),
		"outputProfiles": LIVE_OUTPUT_PROFILES or PROFILE_GROUP_INFO.get("outputProfiles")
	}

	if DEBUG:
		print(f"API_URL: {API_URL}\nMETHOD: PUT\nBODY: {json.dumps(BODY, indent=4)}")

	try:
		RESPONSE = requests.put(API_URL, headers=HEADERS, data=json.dumps(BODY))

		if not RESPONSE.ok:
			raise Exception()

		return RESPONSE.json()
	except:
		_api_exception_handler(RESPONSE, "Update Live Output Profile Group Failed")