from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _get_media_builder_ids_from_asset(AUTH_TOKEN, URL, SOURCE_ASSET_ID, DEBUG):

	API_URL = f"{URL}/api/mediaBuilder/idsbysource/{SOURCE_ASSET_ID}"

	HEADERS = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {AUTH_TOKEN}"
	}


	if DEBUG:
		print(f"API_URL: {API_URL}\nMETHOD: GET")

	try:
		RESPONSE = requests.get(API_URL, headers=HEADERS)

		if not RESPONSE.ok:
			raise Exception()

		return RESPONSE.json()
	except:
		_api_exception_handler(RESPONSE, "Get Media Builder Ids From Asset Failed")