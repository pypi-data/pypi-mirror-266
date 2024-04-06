from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import json, os, requests

def _start_upload(AUTH_TOKEN, URL, NAME, EXISTING_ASSET_ID, RELATED_CONTENT_ID, 
                  UPLOAD_OVERWRITE_OPTION, FILE, PARENT_ID, LANGUAGE_ID, DEBUG):

    API_URL = f"{URL}/api/asset/upload/start"
    FILE_STATS = os.stat(FILE)


    FILE_NAME = os.path.basename(FILE)

    CHUNK_SIZE = 8388608
        
    # Create header for the request
    HEADERS = {
  	    "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    # Build the payload BODY
    BODY = {
        "displayName": NAME or FILE_NAME,
      	"contentLength":FILE_STATS.st_size,
      	"uploadOverwriteOption": UPLOAD_OVERWRITE_OPTION,
      	"chunkSize": CHUNK_SIZE,
      	"relativePath": FILE_NAME,
        "parentId":	PARENT_ID,
        "existingAssetId": EXISTING_ASSET_ID,
        "relatedContentId": RELATED_CONTENT_ID,
        "languageId": LANGUAGE_ID,
        "uploadOverwriteOption": UPLOAD_OVERWRITE_OPTION
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST,\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()

        return RESPONSE.json()

    except:
        _api_exception_handler(RESPONSE, "Start asset upload failed")

