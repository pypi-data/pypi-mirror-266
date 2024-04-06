from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

def _rename_content_group(AUTH_TOKEN, URL, ID, NAME, DEBUG):
  
	API_URL = f"{URL}/api/contentGroup/{ID}"
	
	HEADERS = {
		"Content-Type": "application/json",
		"Authorization": "Bearer " + AUTH_TOKEN
	}
	
	BODY = {
		"Name": NAME
	}
	
	if DEBUG:
		print(f"URL: {API_URL},\nMETHOD: PATCH\nBODY: {json.dumps(BODY, indent=4)}")
	
	try:
		RESPONSE = requests.patch(API_URL, headers=HEADERS, data=json.dumps(BODY))
		if not RESPONSE.ok:
			raise Exception()
	
		return RESPONSE.json()
	
	except:
		_api_exception_handler(RESPONSE, "Rename content group failed")