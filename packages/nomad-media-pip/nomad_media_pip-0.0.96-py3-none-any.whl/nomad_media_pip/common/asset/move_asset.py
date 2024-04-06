from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _move_asset(AUTH_TOKEN, URL, ASSET_ID, DESTINATION_FOLDER_ID, BATCH_ACTION,
                CONTENT_DEFINITION_ID, SCHEMA_NAME, USER_ID, RESOLVER_EXCEMPT, DEBUG):
    
    API_URL = f"{URL}/api/admin/asset/{ASSET_ID}/move"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "actionArguments": {
            "destinationFolderAssetId": DESTINATION_FOLDER_ID
        },
        "targetIds": [ASSET_ID],
        "batchAction": BATCH_ACTION,
        "contentDefinitionId": CONTENT_DEFINITION_ID,
        "schemaName": SCHEMA_NAME,
        "userId": USER_ID,
        "resolverExempt": RESOLVER_EXCEMPT
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
    
    except:
        _api_exception_handler(RESPONSE, "Move asset failed")