from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_media_builder_items_add_annotations(AUTH_TOKEN, URL, MEDIA_BUILDER_ID, SOURCE_ASSET_ID, DEBUG):

	API_URL = f"{URL}/api/mediaBuilder/{MEDIA_BUILDER_ID}/items/{SOURCE_ASSET_ID}/add-annotations"

	HEADERS = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {AUTH_TOKEN}"
	}

	if DEBUG:
		print(f"API_URL: {API_URL}\nMETHOD: POST")

	try:
		RESPONSE = requests.post(API_URL, headers=HEADERS)

		if not RESPONSE.ok:
			raise Exception()

		return RESPONSE.json()
	except:
		_api_exception_handler(RESPONSE, "Create Media Builder Items Add Annotations Failed")