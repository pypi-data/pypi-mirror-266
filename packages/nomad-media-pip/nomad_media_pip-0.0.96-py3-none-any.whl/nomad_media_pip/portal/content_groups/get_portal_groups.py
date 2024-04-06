from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, requests

def _get_portal_groups(AUTH_TOKEN, URL, RETURNED_GROUP_NAMES, DEBUG):
	API_URL = f"{URL}/api/portal/groups"

	HEADERS = {
		"Content-Type": "application/json",
		"Authorization": "Bearer " + AUTH_TOKEN
	}

	BODY = {
		"returnedGroupNames": RETURNED_GROUP_NAMES
	}

	if DEBUG:
		print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

	try:
		RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

		if not RESPONSE.ok:
			raise Exception()

		return RESPONSE.json()

	except:
		_api_exception_handler(RESPONSE, "Get poral groups failed: ")