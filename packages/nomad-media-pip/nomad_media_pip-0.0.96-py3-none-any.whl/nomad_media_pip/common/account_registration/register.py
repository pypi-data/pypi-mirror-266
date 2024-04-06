from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json
import requests

def _register(URL, EMAIL, FIRST_NAME, LAST_NAME, PASSWORD, DEBUG):

	API_URL = f"{URL}/api/account/register"

	HEADERS = {
		"Content-Type": "application/json"
	}

	# replace username and password with your username and password
	BODY = {
		"firstName": FIRST_NAME,
		"lastName": LAST_NAME,
		"email": EMAIL,
		"password": PASSWORD
	}

	if DEBUG:
		print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

	try:
		RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

		if not RESPONSE.ok:
			raise Exception()

		return RESPONSE.json()

	except:
		raise Exception(RESPONSE, "Register user failed")
            
