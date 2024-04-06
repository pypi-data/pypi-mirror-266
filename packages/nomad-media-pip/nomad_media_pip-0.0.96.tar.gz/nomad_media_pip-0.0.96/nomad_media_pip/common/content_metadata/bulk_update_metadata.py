from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.common.search.post_search import _post_search

import requests, json

def _bulk_update_metadata(AUTH_TOKEN, URL, CONTENT_IDS, COLLECTION_IDS, RELATED_CONTENT_IDS, 
                          TAG_IDS, SCHEMA_NAME, DEBUG):
    
    API_URL = f"{URL}/api/admin/content/bulk-metadata-update"

    META_DATA = _post_search(AUTH_TOKEN, URL, None, None, None,
                            [
                                {
                                    "fieldName": "id",
                                    "operator": "Equals",
                                    "values": CONTENT_IDS
                                }
                            ], None, None, None, None, None, None, True, DEBUG)["items"]

    if META_DATA:
        COLLECTIONS, RELATED_CONTENTS, TAGS = [], [], []

        for META_DATA_item in META_DATA:
            COLLECTIONS += [item.get("id", None) for item in META_DATA_item.get("collections", [])]
            RELATED_CONTENTS += [item.get("id", None) for item in META_DATA_item.get("relatedContents", [])]
            TAGS += [item.get("id", None) for item in META_DATA_item.get("tags", [])]

    COLLECTIONS += COLLECTION_IDS if COLLECTION_IDS is not None else []
    RELATED_CONTENTS += RELATED_CONTENT_IDS if RELATED_CONTENT_IDS is not None else []
    TAGS += TAG_IDS if TAG_IDS is not None else []

    COLLECTIONS = list(set(COLLECTIONS))
    RELATED_CONTENTS = list(set(RELATED_CONTENTS))
    TAGS = list(set(TAGS))


    # Create header for the request
    HEADERS = {
        "Authorization": "Bearer " + AUTH_TOKEN,
        "Content-Type": "application/json"
    }

    BODY = {
        "contents": CONTENT_IDS,
        "collections": COLLECTIONS,
        "relatedContents": RELATED_CONTENTS,
        "tags": TAGS,
    }

    if DEBUG:
        print(f"URL: {API_URL},\nMETHOD: POST\nBODY: {json.dumps(BODY, indent= 4)}")

    try:
        # Send the request
        RESPONSE = requests.post(API_URL, headers= HEADERS, data= json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
    
    except:
        _api_exception_handler(RESPONSE, "Bulk update metadata failed")