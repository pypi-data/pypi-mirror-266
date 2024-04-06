from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler

import requests, json

def _add_saved_search(AUTH_TOKEN, URL, NAME, FEATURED, BOOKMARKED, PUBLIC, SEQUENCE, TYPE,
                      QUERY, OFFSET, SIZE, FILTERS, SORT_FIELDS, SEARCH_RESULT_FIELDS,
                      SIMILAR_ASSET_ID, MIN_SCORE, EXCLUDE_TOTAL_RECORD_COUNT, FILTER_BINDER,
                      DEBUG):
    
    API_URL = f"{URL}/api/portal/savedsearch"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    BODY = {
        "name": NAME,
        "featured": FEATURED,
        "bookmarked": BOOKMARKED,
        "public": PUBLIC,
        "pageSize": SIZE,
        "sequence": SEQUENCE,
        "type": TYPE,
        "criteria": {}
    }

    if QUERY: BODY["criteria"]["query"] = QUERY
    BODY["criteria"]["pageOffset"] = OFFSET if OFFSET else 0
    BODY["criteria"]["pageSize"] = SIZE if SIZE else 10
    if FILTERS: BODY["criteria"]["filters"] = FILTERS
    if SORT_FIELDS: BODY["criteria"]["sortFields"] = SORT_FIELDS
    if SEARCH_RESULT_FIELDS: BODY["criteria"]["searchResultFields"] = SEARCH_RESULT_FIELDS
    if SIMILAR_ASSET_ID: BODY["criteria"]["similarAssetId"] = SIMILAR_ASSET_ID
    if MIN_SCORE: BODY["criteria"]["minScore"] = MIN_SCORE
    if EXCLUDE_TOTAL_RECORD_COUNT: BODY["criteria"]["excludeTotalRecordCount"] = EXCLUDE_TOTAL_RECORD_COUNT
    if FILTER_BINDER: BODY["criteria"]["filterBinder"] = FILTER_BINDER

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: POST\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.post(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Add saved search failed")