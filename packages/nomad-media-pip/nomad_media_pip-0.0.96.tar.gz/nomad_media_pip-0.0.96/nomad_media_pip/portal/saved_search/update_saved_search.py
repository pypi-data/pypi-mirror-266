from nomad_media_pip.exceptions.api_exception_handler import _api_exception_handler
from nomad_media_pip.portal.saved_search.get_saved_search import _get_saved_search

import requests, json

def _update_saved_search(AUTH_TOKEN, URL, ID, NAME, FEATURED, BOOKMARKED, PUBLIC, SEQUENCE, 
                         TYPE, QUERY, OFFSET, SIZE, FILTERS, SORT_FIELDS, 
                         SEARCH_RESULT_FIELDS, SIMILAR_ASSET_ID, MIN_SCORE, 
                         EXCLUDE_TOTAL_RECORD_COUNT, FILTER_BINDER, DEBUG):
    
    API_URL = f"{URL}/api/portal/savedsearch/{ID}"

    HEADERS = {
        "Content-Type": "application/json",
      	"Authorization": "Bearer " + AUTH_TOKEN
    }

    SAVED_SEARCH_INFO = _get_saved_search(AUTH_TOKEN, URL, ID, DEBUG)

    BODY = {
        key: value for key, value in {
            "id": ID,
            "name": NAME or SAVED_SEARCH_INFO.get("name"),
            "featured": FEATURED or SAVED_SEARCH_INFO.get("featured"),
            "bookmarked": BOOKMARKED or SAVED_SEARCH_INFO.get("bookmarked"),
            "public": PUBLIC or SAVED_SEARCH_INFO.get("public"),
            "pageSize": SIZE or SAVED_SEARCH_INFO.get("pageSize"),
            "sequence": SEQUENCE or SAVED_SEARCH_INFO.get("sequence"),
            "type": TYPE or SAVED_SEARCH_INFO.get("type"),
            "user": SAVED_SEARCH_INFO.get("user"),
            "criteria": {
                key : value for key, value in {
                    "query": QUERY or SAVED_SEARCH_INFO.get("criteria").get("query"),
                    "pageOffset": OFFSET or SAVED_SEARCH_INFO.get("criteria").get("pageOffset"),
                    "pageSize": SIZE or SAVED_SEARCH_INFO.get("criteria").get("pageSize"),
                    "filters": FILTERS or SAVED_SEARCH_INFO.get("criteria").get("filters"),
                    "sortFields": SORT_FIELDS or SAVED_SEARCH_INFO.get("criteria").get("sortFields"),
                    "searchResultFields": SEARCH_RESULT_FIELDS or SAVED_SEARCH_INFO.get("criteria").get("searchResultFields"),
                    "similarAssetId": SIMILAR_ASSET_ID or SAVED_SEARCH_INFO.get("criteria").get("similarAssetId"),
                    "minScore": MIN_SCORE or SAVED_SEARCH_INFO.get("criteria").get("minScore"),
                    "excludeTotalRecordCount": EXCLUDE_TOTAL_RECORD_COUNT or SAVED_SEARCH_INFO.get("criteria").get("excludeTotalRecordCount"),
                    "filterBinder": FILTER_BINDER or SAVED_SEARCH_INFO.get("criteria").get("filterBinder")
                }.items() if value is not None
            }
        }.items() if value is not None
    }

    if DEBUG:
        print(f"URL: {API_URL}\nMETHOD: PUT\nBODY: {json.dumps(BODY, indent=4)}")

    try:
        RESPONSE = requests.put(API_URL, headers=HEADERS, data=json.dumps(BODY))

        if not RESPONSE.ok:
            raise Exception()
        
        return RESPONSE.json()
    
    except:
        _api_exception_handler(RESPONSE, "Update saved search failed")