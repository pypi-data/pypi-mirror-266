from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _register_asset(AUTH_TOKEN, URL, ASSET_ID, PARENT_ID, DISPLAY_OBJECT_KEY, BUCKET_NAME,
                    OBJECT_KEY, ETAG, TAGS, COLLECTIONS, RELATED_CONTENTS, SEQUENCER,
                    ASSET_STATUS, STORAGE_CLASS, ASSET_TYPE, CONTENT_LENGTH, STORAGE_EVENT_NAME,
                    CREATED_DATE, STORAGE_SOURCE_IP_ADDRESS, START_MEDIA_PROCESSOR,
                    DELETE_MISSING_ASSET, DEBUG):
    
    API_URL = f"{URL}/api/admin/asset/register"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    DATA = {
        "id": ASSET_ID,
        "parentId": PARENT_ID,
        "displayObjectKey": DISPLAY_OBJECT_KEY,
        "bucketName": BUCKET_NAME,
        "objectKey": OBJECT_KEY,
        "eTag": ETAG,
        "tags": TAGS,
        "collections": COLLECTIONS,
        "relatedContents": RELATED_CONTENTS,
        "sequencer": SEQUENCER,
        "assetStatus": ASSET_STATUS,
        "storageClass": STORAGE_CLASS,
        "assetType": ASSET_TYPE,
        "contentLength": CONTENT_LENGTH,
        "storageEventName": STORAGE_EVENT_NAME,
        "createdDate": CREATED_DATE,
        "storageSourceIpAddress": STORAGE_SOURCE_IP_ADDRESS,
        "startMediaProcessor": START_MEDIA_PROCESSOR,
        "deleteMissingAsset": DELETE_MISSING_ASSET
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(DATA))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Register asset failed")