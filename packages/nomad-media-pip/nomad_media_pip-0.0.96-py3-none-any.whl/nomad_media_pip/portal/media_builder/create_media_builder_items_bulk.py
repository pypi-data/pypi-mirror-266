from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _create_media_builder_items_bulk(AUTH_TOKEN, URL, MEDIA_BUILDER_ID, MEDIA_BUILDER_ITEMS, DEBUG):

	API_URL = f"{URL}/api/mediaBuilder/{MEDIA_BUILDER_ID}/items/bulk"

	HEADERS = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {AUTH_TOKEN}"
	}

	BODY = MEDIA_BUILDER_ITEMS
	

	if DEBUG:
		print(f"API_URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

	try:
		RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

		if not RESPONSE.ok:
			raise Exception()

		return RESPONSE.json()
	except:
		_api_exception_handler(RESPONSE, "Create Media Builder Items Bulk Failed")